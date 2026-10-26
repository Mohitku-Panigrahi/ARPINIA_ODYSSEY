# PDF GENERATION CONTRACT

The Frontend (Pod C) is responsible for generating the final ARPINIA ODYSSEY branded PDF report.

## Data Merging Rules
The PDF combines two distinct data sources:
1. **DETERMINISTIC EVIDENCE (`evidence.schema.json`)**: Contains incident ID, timestamps, coordinates, SAR area, candidate ranks, probabilities, and attribution scores.
2. **AI INTERPRETATION (`llm-interpretation.schema.json`)**: Contains narrative summaries, plain-english explanations, and next-step recommendations.

## Strict Separation
- The PDF MUST visually distinguish AI-generated text from deterministic numerical evidence.
- Numerical values (ranks, scores, coords) MUST be sourced exclusively from the Evidence JSON. The LLM narrative must not overwrite them.
