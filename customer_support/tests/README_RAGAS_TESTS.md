# Retail Regulation Quiz - Ragas Evaluation Tests

## Overview

This test suite evaluates the RAG (Retrieval-Augmented Generation) system's ability to answer complex regulatory questions about retail food regulation, consumer product safety, and tobacco retail policies using the **Ragas evaluation framework**.

## Test File

`test_retail_regulation_quiz.py` - Comprehensive test suite with 9 quiz questions

## Quiz Questions Coverage

The quiz covers three main regulatory areas:

### 1. **Retail Food Regulation (NEHA Policy)**
- Foodborne disease economic costs
- Leading causes of foodborne illness outbreaks
- FDA Retail Program Standards resources

### 2. **Consumer Product Safety (CPSC Handbook)**
- General Conformity Certificate (GCC) requirements
- Civil penalties under the Consumer Product Safety Act
- Criminal penalties under the Flammable Fabrics Act

### 3. **Tobacco Retail Regulations**
- Minimum pack size requirements for cigarettes
- Federal restrictions on health descriptors
- Warning label requirements for smokeless tobacco

## Test Suite Structure

### 1. `test_retrieve_contexts_for_quiz_questions` ✅
**Purpose:** Verify the retrieval system can fetch relevant contexts

**What it tests:**
- Retrieves contexts for all 9 quiz questions
- Validates context count and relevance scores
- Ensures reranking is working properly

**Expected Results:**
- All questions retrieve 5 contexts
- Relevance scores between 0.45 - 0.75

### 2. `test_answer_quiz_questions_with_rag`
**Purpose:** Generate answers using RAG system

**What it tests:**
- Context retrieval
- Answer generation using LLM
- Comparison with ground truth answers

**Scope:** Tests first 3 questions for efficiency

### 3. `test_evaluate_quiz_with_ragas_metrics` (Full Ragas Evaluation)
**Purpose:** Comprehensive evaluation with Ragas metrics

**Ragas Metrics Used:**
- **Faithfulness** - Answers are grounded in retrieved contexts
- **Context Precision** - Relevant contexts ranked higher
- **Context Recall** - All relevant contexts are retrieved
- **Answer Relevancy** - Answers are relevant to the question
- **Factual Correctness** - Answers match ground truth

**Output:**
- Summary metrics (average scores)
- Detailed per-question scores
- CSV export of results

### 4. `test_individual_question_faithfulness`
**Purpose:** Deep dive into faithfulness metric

**What it tests:**
- Single question faithfulness evaluation
- Ensures answers don't hallucinate
- Validates context grounding

### 5. `test_retrieval_performance_metrics`
**Purpose:** Performance benchmarking

**Metrics Tracked:**
- Retrieval time per question (ms)
- Average relevance scores
- Number of contexts retrieved

## Running the Tests

### Prerequisites

```bash
# Install dependencies
pip install ragas langchain-openai datasets

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export NVIDIA_API_KEY="your-nvidia-api-key"
```

### Run All Tests

```bash
cd /workspaces/NVDIA-Retail-AI-Teams/customer_support
python -m pytest tests/test_retail_regulation_quiz.py -v -s
```

### Run Specific Tests

```bash
# Context retrieval only
pytest tests/test_retail_regulation_quiz.py::test_retrieve_contexts_for_quiz_questions -v -s

# Ragas evaluation only
pytest tests/test_retail_regulation_quiz.py::test_evaluate_quiz_with_ragas_metrics -v -s -m ragas

# Performance metrics only
pytest tests/test_retail_regulation_quiz.py::test_retrieval_performance_metrics -v -s
```

### Run by Test Markers

```bash
# Register custom markers in pytest.ini first, then:
pytest tests/test_retail_regulation_quiz.py -m slow -v -s
pytest tests/test_retail_regulation_quiz.py -m ragas -v -s
pytest tests/test_retail_regulation_quiz.py -m performance -v -s
```

## Test Results

### Context Retrieval Results ✅

All 9 questions successfully retrieved relevant contexts:

| Question Topic | Contexts | Top Score |
|---------------|----------|-----------|
| Foodborne disease cost | 5 | 0.5739 |
| GCC requirements | 5 | 0.4529 |
| Cigarette pack size | 5 | 0.5571 |
| Foodborne illness causes | 5 | 0.7496 |
| CPSA civil penalties | 5 | 0.6538 |
| Health descriptors restriction | 5 | 0.6083 |
| RFFM Grant Program | 5 | 0.6761 |
| FFA criminal penalties | 5 | 0.6096 |
| Tobacco warning labels | 5 | 0.7293 |

**Average Relevance Score:** 0.614

### Expected Ragas Metrics (To Be Run)

| Metric | Expected Threshold | Description |
|--------|-------------------|-------------|
| Faithfulness | > 0.5 | Answers grounded in contexts |
| Context Precision | > 0.4 | Relevant contexts ranked high |
| Context Recall | > 0.6 | All relevant contexts retrieved |
| Answer Relevancy | > 0.5 | Answers address the question |
| Factual Correctness | > 0.6 | Answers match ground truth |

## Quiz Questions & Ground Truth

Each quiz question includes:
- **question** - The regulatory question
- **ground_truth** - Expert-verified answer
- **reference** - Source document and page numbers

Example:
```python
{
    "question": "What is the estimated annual economic cost of foodborne disease?",
    "ground_truth": "$17.6 billion...",
    "reference": "NEHA Policy Statement, Page 3"
}
```

## Key Features

### 1. **Modular Test Design**
- Each test can run independently
- Progressive complexity (retrieval → generation → evaluation)
- Reusable fixtures

### 2. **Comprehensive Evaluation**
- Multiple Ragas metrics
- Performance benchmarking
- Detailed reporting

### 3. **Production-Ready**
- Error handling
- Timeout management
- CSV export for analysis

### 4. **Configurable**
- Adjustable thresholds
- Customizable test scope
- Flexible metrics selection

## Interpreting Results

### Faithfulness Score
- **High (>0.7):** Answers are well-grounded in context
- **Medium (0.5-0.7):** Mostly grounded, some extrapolation
- **Low (<0.5):** Possible hallucinations

### Context Precision
- **High (>0.6):** Retrieval system ranks relevant docs highly
- **Medium (0.4-0.6):** Some irrelevant docs in top results
- **Low (<0.4):** Retrieval needs improvement

### Answer Relevancy
- **High (>0.7):** Answers directly address the question
- **Medium (0.5-0.7):** Answers partially on-topic
- **Low (<0.5):** Answers miss the point

## Troubleshooting

### Issue: "No contexts retrieved"
- **Solution:** Ensure Qdrant is running with data
- **Check:** `docker ps` to verify Qdrant container

### Issue: "OPENAI_API_KEY not set"
- **Solution:** Export your OpenAI API key
- **Command:** `export OPENAI_API_KEY=your-key`

### Issue: "Async errors"
- **Solution:** Ensure retrieval.py properly handles sync/async
- **Fixed:** Now uses `run_in_executor` for sync calls

### Issue: "Tests timing out"
- **Solution:** Reduce test scope (use first 3 questions)
- **Adjust:** `test_questions = QUIZ_DATA[:3]`

## Future Enhancements

1. **Add More Metrics**
   - Response Time
   - Token Usage
   - Cost Analysis

2. **Expand Quiz**
   - Add 20+ questions
   - Cover more regulatory areas
   - Include edge cases

3. **Continuous Evaluation**
   - CI/CD integration
   - Automated benchmarking
   - Performance regression detection

4. **Advanced Analysis**
   - Per-document performance
   - Query complexity analysis
   - Error pattern detection

## References

- **Ragas Documentation:** https://docs.ragas.io/
- **NEHA Policy Statement:** Retail Program Standards
- **CPSC Handbook:** Regulated Products Handbook
- **Tobacco Fact Sheet:** Federal Regulation of Tobacco

## License

This test suite is part of the NVIDIA Retail AI Teams project.

---

**Last Updated:** November 3, 2025  
**Test Framework:** Ragas v0.3.8  
**Python Version:** 3.12.1
