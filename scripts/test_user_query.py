import sys
import os
sys.path.append(os.getcwd())

from ai.agent import app
from langchain_core.messages import HumanMessage

def test_user_query():
    query = "show me all abnormal results for subject 10014354"
    print(f"\n--- Testing User Query: '{query}' ---")
    
    # Run the graph
    inputs = {"question": query}
    # For testing, we just run the graph to see the state after nodes
    result = app.invoke(inputs)
    
    print(f"Intent identified: {result['intent']}")
    print(f"Entities: {result['entities']}")
    print(f"Context found: {len(result.get('context', []))} chunks")
    
    if result.get('context'):
        print("First chunk sample:")
        print(result['context'][0][:200] + "...")
        
    print(f"Aggregation result: {result.get('numerical_result')}")
    print("-" * 40)

if __name__ == "__main__":
    test_user_query()
