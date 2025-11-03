# Retail Regulation Quiz Tests - Quick Reference

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install ragas langchain-openai datasets pytest pytest-asyncio

# 2. Set API keys
export OPENAI_API_KEY="your-key"
export NVIDIA_API_KEY="your-key"

# 3. Run tests
cd /workspaces/NVDIA-Retail-AI-Teams/customer_support
pytest tests/test_retail_regulation_quiz.py -v
```

## 📋 Test Commands

### Individual Tests

```bash
# Context retrieval (fastest, ~8s)
pytest tests/test_retail_regulation_quiz.py::test_retrieve_contexts_for_quiz_questions -v -s

# Answer generation with RAG (~30s)
pytest tests/test_retail_regulation_quiz.py::test_answer_quiz_questions_with_rag -v -s

# Full Ragas evaluation (~2-3 min)
pytest tests/test_retail_regulation_quiz.py::test_evaluate_quiz_with_ragas_metrics -v -s

# Faithfulness test (~15s)
pytest tests/test_retail_regulation_quiz.py::test_individual_question_faithfulness -v -s

# Performance metrics (~10s)
pytest tests/test_retail_regulation_quiz.py::test_retrieval_performance_metrics -v -s
```

### By Marker

```bash
# Run only Ragas tests
pytest tests/test_retail_regulation_quiz.py -m ragas -v -s

# Run only fast tests
pytest tests/test_retail_regulation_quiz.py -m "not slow" -v

# Run performance tests
pytest tests/test_retail_regulation_quiz.py -m performance -v
```

### All Tests

```bash
# Run everything
pytest tests/test_retail_regulation_quiz.py -v -s

# Run with summary
pytest tests/test_retail_regulation_quiz.py -v --tb=short
```

## 📊 Expected Results

### ✅ Context Retrieval Test
```
PASSED ✓
All 9 questions retrieve 5 contexts each
Average relevance score: 0.614
Time: ~8 seconds
```

### ✅ Ragas Evaluation (When Run with OpenAI Key)
```
Metrics:
- Faithfulness: >0.5 (answers grounded in context)
- Context Precision: >0.4 (relevant docs ranked high)
- Context Recall: >0.6 (all relevant docs retrieved)
- Answer Relevancy: >0.5 (answers on-topic)
- Factual Correctness: >0.6 (matches ground truth)

Output: tests/ragas_quiz_results.csv
Time: ~2-3 minutes for 5 questions
```

## 🎯 Quiz Coverage

**9 Questions across 3 categories:**

### Retail Food Regulation (3 questions)
- ✅ Foodborne disease economic costs ($17.6B)
- ✅ Five leading causes of outbreaks
- ✅ NEHA-FDA Grant Program resources

### Consumer Product Safety (3 questions)
- ✅ General Conformity Certificate requirements
- ✅ CPSA civil penalties ($100K/$15.15M)
- ✅ Flammable Fabrics Act penalties

### Tobacco Retail Regulations (3 questions)
- ✅ Minimum pack size (20 cigarettes)
- ✅ Health descriptor restrictions
- ✅ Warning label requirements (20% coverage)

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| No contexts retrieved | Ensure Qdrant has data: `docker ps` |
| OpenAI key missing | `export OPENAI_API_KEY=your-key` |
| Tests timeout | Reduce scope in test (use [:3]) |
| Async errors | Fixed in retrieval.py v2 |
| Import errors | `pip install -r requirements.txt` |

## 📁 Key Files

```
customer_support/
├── tests/
│   ├── test_retail_regulation_quiz.py    # Main test suite
│   ├── test_retrieval.py                 # Unit tests
│   ├── README_RAGAS_TESTS.md            # Full documentation
│   └── ragas_quiz_results.csv           # Output (after Ragas run)
├── pytest.ini                            # Pytest configuration
└── requirements.txt                      # Dependencies
```

## 🔍 Understanding Scores

### Faithfulness (0.0 - 1.0)
- **0.8-1.0:** Excellent - fully grounded
- **0.6-0.8:** Good - mostly grounded
- **0.4-0.6:** Fair - some extrapolation
- **<0.4:** Poor - possible hallucinations

### Context Precision (0.0 - 1.0)
- **0.7-1.0:** Excellent retrieval
- **0.5-0.7:** Good retrieval
- **0.3-0.5:** Fair - needs tuning
- **<0.3:** Poor - retrieval broken

### Answer Relevancy (0.0 - 1.0)
- **0.8-1.0:** Perfectly on-topic
- **0.6-0.8:** Mostly relevant
- **0.4-0.6:** Partially relevant
- **<0.4:** Off-topic

## 💡 Tips

1. **Start with retrieval test** - Fast validation
2. **Use --tb=short** - Cleaner error messages
3. **Run Ragas tests separately** - They take longer
4. **Check CSV output** - Detailed per-question analysis
5. **Monitor token usage** - OpenAI costs can add up

## 📊 Sample Output

```
CONTEXT RETRIEVAL SUMMARY
=========================
Question: What is the estimated annual economic cost...
  Contexts Retrieved: 5
  Top Score: 0.5739

Question: What are the key requirements for a GCC...
  Contexts Retrieved: 5
  Top Score: 0.4529

...

✓ All questions retrieved contexts successfully!
Average relevance: 0.614
Test time: 7.62s
```

## 🎓 Learning Resources

- **Ragas Docs:** https://docs.ragas.io/
- **Evaluation Guide:** https://docs.ragas.io/en/latest/concepts/metrics/
- **LangChain + Ragas:** https://docs.ragas.io/en/latest/howtos/integrations/langchain.html

## 📝 Notes

- **OpenAI API:** Required for full Ragas evaluation
- **NVIDIA API:** Required for embeddings and reranking
- **Qdrant:** Must be running with processed documents
- **Python:** Requires 3.12+ for best compatibility

---

**Quick Test:** `pytest tests/test_retail_regulation_quiz.py::test_retrieve_contexts_for_quiz_questions -v`

**Full Evaluation:** `pytest tests/test_retail_regulation_quiz.py -m ragas -v -s`
