/** Validate the 36 frozen sources and count Gemma's formatted input tokens. No inference. */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { Chat, LMStudioClient } = require('/Users/sam/.lmstudio/extensions/plugins/lmstudio/js-code-sandbox/node_modules/@lmstudio/sdk/dist/index.cjs');

const ROOT = path.resolve(__dirname, '../..');
const CORPUS_SHA = 'df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a';
const SAMPLE_SHA = 'be2411dd73cfcb20c7e55b9fda2aca02a07e05cbf8e8c335a172e6402672d29c';
const PROMPT_SHA = 'a8a84c7d3640ce11249e107717a11e24499592c70f24dc2215bc9305b9949889';
const FORMAT_SHA = '65ee03d0a90267593885b0982684a55a9d7f7d40e7ce2a505d3c3c663a72b3a1';
const MAX_OUTPUT_TOKENS = 8192;
const MODEL = 'google/gemma-4-31b-qat';

function sha(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function frozen(name, expected) {
  const value = fs.readFileSync(path.join(ROOT, name));
  if (sha(value) !== expected) throw new Error(`Frozen input changed: ${name}`);
  return value;
}

async function main() {
  const corpus = new Map(frozen('data/cleaned/bills.jsonl', CORPUS_SHA)
    .toString('utf8').split('\n').filter(Boolean).map(line => {
      const row = JSON.parse(line); return [row.bill_number, row];
    }));
  const sample = JSON.parse(frozen('data/full/sample.json', SAMPLE_SHA));
  const prompt = frozen('prompts/pilot-summary-v1.txt', PROMPT_SHA).toString('utf8');
  const format = JSON.parse(frozen('prompts/pilot-summary-v1.format.json', FORMAT_SHA));
  if (sample.source_sha256 !== CORPUS_SHA || sample.selected.length !== 36 ||
      format.type !== 'json_schema' || format.strict !== true) {
    throw new Error('Frozen sample or format mismatch');
  }
  const client = new LMStudioClient();
  const model = await client.llm.model(MODEL);
  const contextLength = await model.getContextLength();
  const rows = [];
  for (const item of sample.selected) {
    const source = corpus.get(item.bill_number);
    if (!source || source.id !== item.id ||
        sha(Buffer.from(source.bill_text, 'utf8')) !== item.bill_text_sha256 ||
        source.bill_text.trim().split(/\s+/).length !== item.word_count) {
      throw new Error(`Source mismatch: ${item.bill_number}`);
    }
    const user = `Bill number: ${item.bill_number}\n\n<bill_text>\n${source.bill_text}\n</bill_text>`;
    const chat = Chat.from([{ role: 'system', content: prompt }, { role: 'user', content: user }]);
    const formatted = await model.applyPromptTemplate(chat);
    const inputTokens = await model.countTokens(formatted);
    rows.push({ bill_number: item.bill_number, cell: item.cell, tertile: item.tertile,
      source_words: item.word_count, source_sha256: item.bill_text_sha256,
      gemma_formatted_input_tokens: inputTokens,
      input_plus_output_allowance: inputTokens + MAX_OUTPUT_TOKENS,
      fits_loaded_context: inputTokens + MAX_OUTPUT_TOKENS <= contextLength });
  }
  const result = { status: rows.every(r => r.fits_loaded_context) ? 'pass' : 'context_insufficient',
    sample_sha256: SAMPLE_SHA, corpus_sha256: CORPUS_SHA,
    prompt_sha256: PROMPT_SHA, format_sha256: FORMAT_SHA,
    model: MODEL, loaded_context_tokens: contextLength, max_output_tokens: MAX_OUTPUT_TOKENS,
    note: 'Counts the model-applied prompt template and tokenizer; grammar/schema overhead may differ from actual request usage.',
    records: rows };
  const output = path.join(ROOT, 'data/extension/full-input-preflight.json');
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
  console.log(`Validated ${rows.length} frozen bills; model context ${contextLength}`);
  console.log(`Largest formatted input: ${Math.max(...rows.map(r => r.gemma_formatted_input_tokens))} tokens`);
  console.log(`Input + output allowance fits: ${rows.filter(r => r.fits_loaded_context).length}/${rows.length}`);
  console.log(`Wrote ${output}`);
  if (result.status !== 'pass') process.exitCode = 1;
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
