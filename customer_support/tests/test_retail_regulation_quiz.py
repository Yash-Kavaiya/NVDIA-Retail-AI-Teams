"""
Test cases for Retail Food Regulation, Consumer Product Safety, and Tobacco Retail Policies
using Ragas evaluation framework.

This test suite evaluates the RAG system's ability to answer complex regulatory questions
using metrics like Faithfulness, Context Precision, Answer Relevancy, and Factual Correctness.
"""

import os
import sys
import pytest
import asyncio
from datasets import Dataset
from typing import List, Dict
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from src.retrieval import RetrievalPipeline

# Ragas imports
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    ContextPrecision,
    ContextRecall,
    AnswerRelevancy,
    FactualCorrectness,
    LLMContextRecall
)
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI


# Quiz questions with ground truth answers
QUIZ_DATA = [
    {
        "question": "According to the NEHA Policy Statement on Enrollment and Conformance with the FDA Voluntary National Retail Food Regulatory Program Standards, what is the estimated annual economic cost of foodborne disease in the United States?",
        "ground_truth": "$17.6 billion. This figure accounts for the public health and economic burden of foodborne illnesses, with more than half of outbreaks linked to retail food services.",
        "reference": "NEHA Policy Statement, Page 3; U.S. Department of Agriculture Economic Research Service, 2023"
    },
    {
        "question": "In the Regulated Products Handbook by the U.S. Consumer Product Safety Commission, what are the key requirements for a General Conformity Certificate (GCC) for regulated products?",
        "ground_truth": "A GCC must certify that a product complies with applicable CPSC-enforced statutes, be based on a reasonable testing program, and be available to relevant parties upon request. It applies to non-children's products and must accompany imported goods electronically if required.",
        "reference": "Regulated Products Handbook, Chapter 1, Pages 9-10"
    },
    {
        "question": "Under the federal regulations outlined in the Tobacco Control Legal Consortium's fact sheet on Federal Regulation of Tobacco, what is the minimum pack size requirement for cigarettes, and why does it aim to reduce youth access?",
        "ground_truth": "Cigarettes must be sold in packages containing no fewer than 20 cigarettes, and retailers cannot break open packs to sell fewer than this quantity. This prevents single or small-quantity sales, which appeal to minors due to their lower price.",
        "reference": "Tobacco Control Act and FDA Regulations, Fact Sheet Page 3"
    },
    {
        "question": "What are the five leading causes of foodborne illness outbreaks in retail food settings identified by the CDC?",
        "ground_truth": "1. Improper holding temperatures of food; 2. Improper cooking temperatures; 3. Contaminated utensils and equipment; 4. Food from unsafe sources; 5. Poor employee health and hygiene. These factors account for a significant portion of outbreaks, with improper handwashing contributing to 30% and failure to exclude ill employees to nearly 46%.",
        "reference": "NEHA Policy Statement, Page 4; Angelo et al., 2017"
    },
    {
        "question": "According to the Regulated Products Handbook, what is the maximum civil penalty under the Consumer Product Safety Act (CPSA) for a knowing violation of section 19?",
        "ground_truth": "Up to $100,000 per violation, with a maximum not exceeding $15.15 million for any related series of violations. This applies to prohibited acts such as failing to report defects or noncompliant products, adjusted for inflation.",
        "reference": "Regulated Products Handbook, Chapter 2, Pages 11-12; 76 Federal Register 71554, November 18, 2011"
    },
    {
        "question": "What federal restriction applies to the use of health descriptors like 'light' or 'low tar' on tobacco products in retail settings?",
        "ground_truth": "Such descriptors are prohibited unless the FDA has specifically approved the marketing, as they mislead consumers about health risks. This applies to cigarettes, smokeless tobacco, roll-your-own tobacco, and potentially other deemed products.",
        "reference": "Fact Sheet Page 4; 21 U.S.C.A. § 387k"
    },
    {
        "question": "What resource is provided through the NEHA-FDA Retail Flexible Funding Model (RFFM) Grant Program for jurisdictions enrolling in the Retail Program Standards?",
        "ground_truth": "A mentorship program developed by the National Association of County and City Health Officials (NACCHO) to assist jurisdictions in achieving conformity with the standards. Additional resources include grants, self-assessment courses, and crosswalks with the Public Health Accreditation Board (PHAB) process.",
        "reference": "NEHA Policy Statement, Page 3"
    },
    {
        "question": "What are the criminal penalties under the Flammable Fabrics Act (FFA) for a knowing and willful violation of sections 3 or 8(b)?",
        "ground_truth": "Imprisonment for not more than five years, a fine up to $100,000 for individuals or $200,000 for organizations (or $250,000/$500,000 if death occurs), or both, under the Criminal Fine Improvements Act of 1987. Asset forfeiture may also apply.",
        "reference": "Regulated Products Handbook, Chapter 2, Page 13; 18 U.S.C. § 3571"
    },
    {
        "question": "What percentage of the advertisement area must smokeless tobacco advertisements, including those in retail stores, cover with warnings according to federal regulations?",
        "ground_truth": "20 percent. These textual warnings, amended by the Tobacco Control Act, depict health risks and must appear on packages and ads; graphic warnings for cigarettes are pending litigation.",
        "reference": "Fact Sheet Page 5; 15 U.S.C.A. § 4402(b)(2)(B)"
    }
]


@pytest.fixture(scope="module")
def config():
    """Create test configuration."""
    return Config.from_env()


@pytest.fixture(scope="module")
def evaluator_llm():
    """Create evaluator LLM for Ragas metrics."""
    # Check if OpenAI API key is set
    if "OPENAI_API_KEY" not in os.environ:
        pytest.skip("OPENAI_API_KEY not set - skipping Ragas evaluation tests")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return LangchainLLMWrapper(llm)


@pytest.fixture(scope="module")
def retrieval_pipeline(config):
    """Create retrieval pipeline."""
    return RetrievalPipeline(config)


@pytest.fixture(scope="module")
def ragas_metrics(evaluator_llm):
    """Initialize Ragas metrics."""
    return [
        Faithfulness(llm=evaluator_llm),
        ContextPrecision(llm=evaluator_llm),
        ContextRecall(llm=evaluator_llm),
        AnswerRelevancy(llm=evaluator_llm),
        FactualCorrectness(llm=evaluator_llm),
    ]


@pytest.mark.asyncio
@pytest.mark.slow
async def test_retrieve_contexts_for_quiz_questions(retrieval_pipeline):
    """
    Test that the retrieval system can fetch relevant contexts for all quiz questions.
    This is a prerequisite test before running full Ragas evaluation.
    """
    results = []
    
    for item in QUIZ_DATA:
        question = item["question"]
        
        # Search for relevant context
        search_results = await retrieval_pipeline.search(
            query=question,
            top_k=5,
            rerank=True
        )
        
        assert len(search_results) > 0, f"No contexts retrieved for question: {question[:100]}..."
        
        # Extract contexts
        contexts = [result["text"] for result in search_results]
        
        results.append({
            "question": question,
            "num_contexts": len(contexts),
            "top_score": search_results[0].get("rerank_score", search_results[0].get("score", 0))
        })
    
    # Print summary
    print("\n" + "="*80)
    print("CONTEXT RETRIEVAL SUMMARY")
    print("="*80)
    for result in results:
        print(f"Question: {result['question'][:80]}...")
        print(f"  Contexts Retrieved: {result['num_contexts']}")
        print(f"  Top Score: {result['top_score']:.4f}")
        print()
    
    # All questions should have retrieved contexts
    assert all(r["num_contexts"] > 0 for r in results), "Some questions failed to retrieve contexts"
    
    await retrieval_pipeline.close()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_answer_quiz_questions_with_rag(retrieval_pipeline, evaluator_llm):
    """
    Test answering quiz questions using RAG system and evaluate with a simple LLM.
    This test generates answers but doesn't run full Ragas evaluation.
    """
    from langchain_openai import ChatOpenAI
    
    if "OPENAI_API_KEY" not in os.environ:
        pytest.skip("OPENAI_API_KEY not set - skipping answer generation test")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    results = []
    
    for item in QUIZ_DATA[:3]:  # Test first 3 questions
        question = item["question"]
        ground_truth = item["ground_truth"]
        
        # Retrieve contexts
        search_results = await retrieval_pipeline.search(
            query=question,
            top_k=5,
            rerank=True
        )
        
        contexts = [result["text"] for result in search_results]
        
        # Generate answer using contexts
        context_text = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts)])
        
        prompt = f"""Based on the following contexts, answer the question accurately and concisely.

{context_text}

Question: {question}

Answer:"""
        
        response = llm.invoke(prompt)
        answer = response.content
        
        results.append({
            "question": question,
            "answer": answer,
            "ground_truth": ground_truth,
            "num_contexts": len(contexts)
        })
        
        print(f"\nQuestion: {question[:100]}...")
        print(f"Answer: {answer[:200]}...")
        print(f"Ground Truth: {ground_truth[:200]}...")
        print("-" * 80)
    
    assert len(results) == 3, "Not all questions were answered"
    await retrieval_pipeline.close()


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.ragas
async def test_evaluate_quiz_with_ragas_metrics(retrieval_pipeline, evaluator_llm, ragas_metrics):
    """
    Full Ragas evaluation of the RAG system on retail regulation quiz questions.
    
    This test:
    1. Retrieves contexts for each question
    2. Generates answers using an LLM
    3. Evaluates using Ragas metrics (Faithfulness, Context Precision, etc.)
    4. Reports detailed scores
    """
    from langchain_openai import ChatOpenAI
    
    if "OPENAI_API_KEY" not in os.environ:
        pytest.skip("OPENAI_API_KEY not set - skipping Ragas evaluation")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Prepare data for Ragas evaluation
    questions = []
    answers = []
    ground_truths = []
    contexts_list = []
    
    # Process first 5 questions to keep test time reasonable
    test_questions = QUIZ_DATA[:5]
    
    print("\n" + "="*80)
    print("GENERATING RAG RESPONSES FOR EVALUATION")
    print("="*80)
    
    for i, item in enumerate(test_questions, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]
        
        print(f"\n[{i}/{len(test_questions)}] Processing: {question[:80]}...")
        
        # Retrieve contexts
        search_results = await retrieval_pipeline.search(
            query=question,
            top_k=5,
            rerank=True
        )
        
        contexts = [result["text"] for result in search_results]
        
        # Generate answer
        context_text = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts)])
        
        prompt = f"""Based on the following contexts from retail regulation documents, answer the question accurately and concisely.

{context_text}

Question: {question}

Provide a detailed answer based on the information in the contexts:"""
        
        response = llm.invoke(prompt)
        answer = response.content
        
        questions.append(question)
        answers.append(answer)
        ground_truths.append(ground_truth)
        contexts_list.append(contexts)
        
        print(f"  ✓ Retrieved {len(contexts)} contexts")
        print(f"  ✓ Generated answer: {answer[:150]}...")
    
    # Create Ragas dataset
    ragas_dataset = Dataset.from_dict({
        "user_input": questions,
        "response": answers,
        "reference": ground_truths,
        "retrieved_contexts": contexts_list
    })
    
    print("\n" + "="*80)
    print("RUNNING RAGAS EVALUATION")
    print("="*80)
    
    # Run evaluation
    result = evaluate(
        dataset=ragas_dataset,
        metrics=ragas_metrics,
        llm=evaluator_llm
    )
    
    # Convert to DataFrame for better display
    results_df = result.to_pandas()
    
    print("\n" + "="*80)
    print("RAGAS EVALUATION RESULTS - SUMMARY METRICS")
    print("="*80)
    
    # Print summary metrics
    for metric_name, score in result.items():
        if isinstance(score, (int, float)):
            print(f"{metric_name}: {score:.4f}")
    
    print("\n" + "="*80)
    print("RAGAS EVALUATION RESULTS - DETAILED SCORES")
    print("="*80)
    print(results_df.to_string())
    
    # Save results
    output_file = "/workspaces/NVDIA-Retail-AI-Teams/customer_support/tests/ragas_quiz_results.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\n✓ Detailed results saved to: {output_file}")
    
    # Assertions for minimum quality thresholds
    summary_metrics = {k: v for k, v in result.items() if isinstance(v, (int, float))}
    
    # Check that we have reasonable scores (adjust thresholds as needed)
    if "faithfulness" in summary_metrics:
        assert summary_metrics["faithfulness"] > 0.5, f"Faithfulness score too low: {summary_metrics['faithfulness']:.4f}"
    
    if "context_precision" in summary_metrics:
        assert summary_metrics["context_precision"] > 0.4, f"Context precision too low: {summary_metrics['context_precision']:.4f}"
    
    if "answer_relevancy" in summary_metrics:
        assert summary_metrics["answer_relevancy"] > 0.5, f"Answer relevancy too low: {summary_metrics['answer_relevancy']:.4f}"
    
    await retrieval_pipeline.close()
    
    print("\n" + "="*80)
    print("✓ RAGAS EVALUATION COMPLETE")
    print("="*80)


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.integration
async def test_individual_question_faithfulness(retrieval_pipeline, evaluator_llm):
    """
    Test faithfulness metric on a single question to ensure the system
    generates answers that are grounded in the retrieved contexts.
    """
    from langchain_openai import ChatOpenAI
    
    if "OPENAI_API_KEY" not in os.environ:
        pytest.skip("OPENAI_API_KEY not set - skipping faithfulness test")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Test with the first question
    test_item = QUIZ_DATA[0]
    question = test_item["question"]
    
    # Retrieve contexts
    search_results = await retrieval_pipeline.search(
        query=question,
        top_k=5,
        rerank=True
    )
    
    contexts = [result["text"] for result in search_results]
    
    # Generate answer
    context_text = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts)])
    
    prompt = f"""Based on the following contexts, answer the question accurately.

{context_text}

Question: {question}

Answer:"""
    
    response = llm.invoke(prompt)
    answer = response.content
    
    # Evaluate faithfulness
    from ragas.dataset_schema import SingleTurnSample
    
    sample = SingleTurnSample(
        user_input=question,
        response=answer,
        retrieved_contexts=contexts
    )
    
    faithfulness_metric = Faithfulness(llm=evaluator_llm)
    score = await faithfulness_metric.single_turn_ascore(sample)
    
    print("\n" + "="*80)
    print("FAITHFULNESS TEST RESULTS")
    print("="*80)
    print(f"Question: {question}")
    print(f"\nAnswer: {answer}")
    print(f"\nFaithfulness Score: {score:.4f}")
    print("="*80)
    
    # Assert minimum faithfulness
    assert score > 0.4, f"Faithfulness score too low: {score:.4f}"
    
    await retrieval_pipeline.close()


@pytest.mark.asyncio
@pytest.mark.performance
async def test_retrieval_performance_metrics(retrieval_pipeline):
    """
    Test retrieval performance metrics like response time and context relevance scores.
    """
    import time
    
    performance_results = []
    
    for item in QUIZ_DATA[:5]:
        question = item["question"]
        
        start_time = time.time()
        search_results = await retrieval_pipeline.search(
            query=question,
            top_k=5,
            rerank=True
        )
        end_time = time.time()
        
        retrieval_time = end_time - start_time
        
        performance_results.append({
            "question": question[:80],
            "retrieval_time_ms": retrieval_time * 1000,
            "num_contexts": len(search_results),
            "avg_score": sum(r.get("rerank_score", r.get("score", 0)) for r in search_results) / len(search_results) if search_results else 0
        })
    
    print("\n" + "="*80)
    print("RETRIEVAL PERFORMANCE METRICS")
    print("="*80)
    
    df = pd.DataFrame(performance_results)
    print(df.to_string(index=False))
    
    avg_time = df["retrieval_time_ms"].mean()
    print(f"\nAverage retrieval time: {avg_time:.2f}ms")
    print(f"Average relevance score: {df['avg_score'].mean():.4f}")
    
    # Performance assertions
    assert avg_time < 5000, f"Average retrieval time too high: {avg_time:.2f}ms"
    assert df["avg_score"].mean() > 0.5, "Average relevance scores too low"
    
    await retrieval_pipeline.close()


if __name__ == "__main__":
    # Run tests with: pytest tests/test_retail_regulation_quiz.py -v -s
    # Run Ragas tests with: pytest tests/test_retail_regulation_quiz.py -v -s -m ragas
    pytest.main([__file__, "-v", "-s"])
