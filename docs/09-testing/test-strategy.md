# Testing Strategy

## Layers
1. **Unit Tests:** Run instantly. Target pure logic (e.g., attribution math).
2. **Integration Tests:** Target DB interactions and API routing.
3. **Golden Scenario Validation:** End-to-end test against SIH-ZENODO-ALPHA. Evaluates output against `ground_truth.json` (test environment only).

## Fixtures Required (`tests/fixtures/`)
- `mock_sar_valid.json`
- `mock_sar_invalid.json`
- `mock_ais_gap.csv`
- `mock_evidence_output.json`
- `mock_llm_response.json`

## CI/CD
- GitHub Actions executes unit tests and schema validations on every PR.
