# Design Notes: Policy Q&A Bot with Grounded Citations

## 1. Chunking Stategy: "Section-Aware" Retrieval

Rather than using simple character-count splitting, this implementation uses a **Recursive Character Text Splitter** with specific hierarchy markers:

- **Separators:** The splitter prioritises breaks at `\nSection`, `\nClause`, and `\n\n`. This ensures that legal clauses are kept whole within a single chunk rather than being sliced in half.
- **Size & Overlap:** A chunk size of **700 tokens** was chosen to provide enough context for the LLM to understand definitions, with a **100-token overlap** to ensure that cross-references (e.g., "subject to Section 4") are captured in adjacent chunks.
- **Metadata Enrichment:** During ingestion, a Regular Expression (Regex) identifies clause markers (e.g., `§3.2` or `Clause 5`). This metadata is "pinned" to the chunk, allowing the bot to provide clause-level citations even if the LLM doesn't explicitly see the heading in the immediate text.

## 2. Robustness & "No Answer" Guardrails

To prevent hallucinations (the AI making up policy rules), I implemented a **Semantic Similarity Threshold**:

- **The Logic:** When a user asks a question, the system calculates the mathematical "distance" between the query and the policy text.
- **The Guardrail:** If the closest match has a distance score greater than 1.1, the system deems the question "out-of-scope" or "unrelated".
- **Behaviour:** Instead of attempting to answer, the bot triggers the mandatory fallback: "_I cannot find a definitive answer in the provided policy wording_".

## 3. Prompt Design

The system uses a **Strict Grounding Prompt**. The instructions explicitly command the model to:

1. Use **only** the provided context.
2. Maintain a neutral, formal tone.
3. Append source citations in the specific format: `Doc_name (Section), p.X`.

## Test Set: 10 Q&A Examples

Use these examples to verify your bot's performance.
| Type | Question | Expected Behaviour |
| :--- | :--- | :--- |
| **In-Domain** | "Is wear-and-tear covered under the policy?" | Provide answer from "Exclusions" section with citation. |
| **In-Domain** | "What is the definition of an 'Insured Person'?" | Provide answer from "Definitions" section with citation. |
| **In-Domain** | "How does the deductible apply to water damage?" | Find "Deductibles" or "Water Damage" clause. |
| **In-Domain** | "What is the waiting period for accidental damage?" | Find "Conditions" or "Waiting Period" section. |
| **In-Domain** | "Are legal fees included in the coverage?" | Search for "Legal Expenses" or "Liability" sections. |
| **Near-Miss** | "Does the policy cover my pet unicorn?" | Trigger "No answer" (Unicorn is not in policy). |
| **Near-Miss** | "Can I claim for damage caused by zombies?" | Trigger "No Answer" (Out of scope). |
| **Near-Miss** | "What is the refund policy if I move to Mars?" | Trigger "No Answer" (Location out of bounds). |
| **Out-of-Scope** | "How do I cook a perfect nasi lemak?" | Trigger Guardrail (Unrelated to insurance). |
| **Out-of-Scope** | "Who won the Olympics in 2024?" | Trigger Guardrail (Unrelated to insurance). |

## Limitations

- I stated that the files can be uploaded to 2-3 PDF files. However, the user only managed to upload one file at a time.
- For **Near-Miss** and **Out-of-Scope**, the behaviours are the same, which are "No answer" instead of giving details about the question's context.
