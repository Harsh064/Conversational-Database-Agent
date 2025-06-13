# Conversational Database Agent with Natural Language Query Mapping using LangChain and MongoDB

# Step 1: Install Required Packages

# Step 2: Load Environment Variables
from typing import List, Dict, Any
from pymongo.collection import Collection
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Step 3: Setup MongoDB Connection
from pymongo import MongoClient
client = MongoClient(MONGODB_URI)
db = client.sample_analytics

# Step 4: Define Query Execution Interface
from langchain.tools import Tool


def get_definition(entity):
    definitions = definitions = {
    "account": "An account represents a customer's financial relationship and includes limits and product types.",
    "transaction": "A transaction is a financial activity like deposits or withdrawals by a customer.",
    
    # Accounts collection
    "limit": "The maximum available credit or transaction limit on the account. It represents the financial ceiling for transactions such as withdrawals or trades.",
    "products": "A list of financial services associated with the account, such as 'brokerage', 'investment', or 'commodity'.",

    # Customers collection
    "tier_and_details": "An embedded document providing details about the customer's membership tier, associated benefits, and whether the tier is currently active.",
    "tier": "The membership level of the customer, such as 'Silver', 'Gold', or 'Platinum', indicating their service level.",
    "benefits": "A list of perks associated with the customer's tier, such as 'priority_support' or 'lower_fees'.",
    "active": "A boolean flag that indicates whether the customer's tier benefits are currently active or inactive.",

    # Transactions collection
    "transaction_count": "The total number of individual transactions stored within a single transaction bucket document.",
    "bucket_start_date": "The earliest date of the transactions stored in a bucket, used for time-based partitioning.",
    "bucket_end_date": "The latest date of the transactions stored in a bucket, used for time-based partitioning.",
    "transaction_code": "A short identifier for the type of transaction. Valid values include 'buy' and 'sell'.",
    "symbol": "The asset's ticker symbol involved in the transaction. Common examples include 'sap', 'team', 'nflx', 'ibm', 'adbe', and 'msft'."
}

    return definitions.get(entity.lower(), "No definition found.")

#functions for accounts section :-

def get_account_limit(account_id: int) -> int:
    """Retrieve the credit or transaction limit of a given account."""
    doc = db.accounts.find_one({"account_id": account_id})
    return doc["limit"] if doc and "limit" in doc else "Limit not found."

def get_account_products(account_id: int) -> List[str]:
    """Return the list of financial products associated with a specific account."""
    doc = db["accounts"].find_one({"account_id": account_id}, {"products": 1})
    if doc and "products" in doc:
        return doc["products"]
    return []

def get_accounts_by_product(product_name: str) -> List[Dict[str, Any]]:
    """Return all accounts that include a specific product type."""
    return list(db.accounts.find({"products": product_name}, {"_id": 0}))

def get_high_limit_accounts(threshold: int = 100000) -> List[Dict[str, Any]]:
    """Return all accounts with a limit greater than the given threshold."""
    return list(db.accounts.find({"limit": {"$gt": threshold}}, {"_id": 0}))

def list_all_account_ids() -> List[int]:
    """Return a list of all account IDs in the system."""
    return [doc["account_id"] for doc in db.accounts.find({}, {"account_id": 1})]



# --- Customers Collection Tools ---
def get_customer_by_username(username):
    return db.customers.find_one({"username": username}, {"_id": 0})

def get_customers_with_email_domain(domain):
    return list(db.customers.find({"email": {"$regex": f"@{domain}$"}}, {"name": 1, "email": 1, "_id": 0}))

def get_customers_by_account(account_id):
    return list(db.customers.find({"accounts": account_id}, {"username": 1, "name": 1, "accounts": 1, "_id": 0}))

def get_accounts_by_customer(username):
    return list(db.customers.find({"username": username}, {"username": 1, "name": 1, "accounts": 1, "_id": 0}))

def get_customer_tiers():
    return list(db.customers.find({}, {"username": 1, "tier_and_details": 1, "_id": 0}))

def get_customers_by_birth_year(year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    return list(db.customers.find({"birthdate": {"$gte": start_date, "$lt": end_date}}, {"name": 1, "birthdate": 1, "_id": 0}))

def get_accounts_by_person_name_or_username(name_or_username: str) -> List[int]:
    """Returns a list of account IDs for a customer identified by name or username."""
    # Search the customers collection for a matching name or username
    customer = db["customers"].find_one({
        "$or": [
            {"name": name_or_username},
            {"username": name_or_username}
        ]
    }, {"customer_id": 1})
    
    if not customer:
        return []

    # Use the customer_id to find all matching accounts
    customer_id = customer["customer_id"]
    accounts = db["accounts"].find(
        {"customer_id": customer_id},
        {"account_id": 1}
    )

    return [acc["account_id"] for acc in accounts]

#Transaction functions :-
def get_transactions_by_account(account_id: int, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
    match = {"account_id": account_id}
    if start_date or end_date:
        match["transactions"] = {
            "$elemMatch": {
                "date": {
                    **({"$gte": datetime.strptime(start_date, "%Y-%m-%d")} if start_date else {}),
                    **({"$lte": datetime.strptime(end_date, "%Y-%m-%d")} if end_date else {})
                }
            }
        }

    buckets = list(db.transactions.find(match))
    transactions = []
    for bucket in buckets:
        for tx in bucket["transactions"]:
            tx_date = tx["date"]
            if (
                (not start_date or tx_date >= datetime.strptime(start_date, "%Y-%m-%d")) and
                (not end_date or tx_date <= datetime.strptime(end_date, "%Y-%m-%d"))
            ):
                transactions.append(tx)
    return transactions

def get_transaction_summary_by_type(account_id: int) -> Dict[str, Dict[str, Any]]:
    buckets = list(db.transactions.find({"account_id": account_id}))
    summary = {}
    for bucket in buckets:
        for tx in bucket["transactions"]:
            code = tx["transaction_code"]
            if code not in summary:
                summary[code] = {"count": 0, "total_value": 0}
            summary[code]["count"] += 1
            summary[code]["total_value"] += float(tx["total"])
    return summary

def get_transactions_by_symbol(account_id: int, symbol: str) -> List[Dict[str, Any]]:
    buckets = list(db.transactions.find({"account_id": account_id}))
    return [
        tx for bucket in buckets
        for tx in bucket["transactions"]
        if tx["symbol"].lower() == symbol.lower()
    ]

def get_transaction_volume_over_time(account_id: int, group_by: str = "month") -> Dict[str, Dict[str, Any]]:
    assert group_by in ["month", "year"], "group_by must be 'month' or 'year'"
    buckets = list(db.transactions.find({"account_id": account_id}))
    result = {}
    for bucket in buckets:
        for tx in bucket["transactions"]:
            dt = tx["date"]
            key = f"{dt.year}" if group_by == "year" else f"{dt.year}-{dt.month:02d}"
            if key not in result:
                result[key] = {"count": 0, "total_value": 0}
            result[key]["count"] += 1
            result[key]["total_value"] += float(tx["total"])
    return result



query_tools = [
    
    Tool(
        name="DefinitionLookup",
        func=lambda x: get_definition(x),
        description="Returns definition of financial terms like account or transaction"
    ),
    
    #tools for accounts
    
    Tool(
        name="GetAccountLimit",
        func=lambda x: str(get_account_limit(int(x))),
        description="Retrieve the credit or transaction limit for a given account ID."
    ),
    Tool(
        name="GetAccountProducts",
        func=lambda x: str(get_account_products(int(x))),
        description="List all financial products associated with a specific account ID."
    ),
    Tool(
        name="GetAccountsByProduct",
        func=lambda x: str(get_accounts_by_product(x)),
        description="Find all accounts that include a specific product type (e.g., 'Derivatives')."
    ),
    Tool(
        name="GetHighLimitAccounts",
        func=lambda x: str(get_high_limit_accounts(int(x) if x else 100000)),
        description="List accounts that have a credit or transaction limit above the given threshold."
    ),
    Tool(
        name="ListAllAccountIDs",
        func=lambda x: str(list_all_account_ids()),
        description="Get a list of all account IDs in the dataset."
    ),
    
    #Customers tools :-
    
    Tool(name="GetCustomerByUsername", func=lambda x: str(get_customer_by_username(x)), description="Get customer details by username"),
    Tool(name="GetCustomersWithEmailDomain", func=lambda x: str(get_customers_with_email_domain(x)), description="List customers with a specific email domain"),
    Tool(name="GetCustomersByAccount", func=lambda x: str(get_customers_by_account(int(x))), description="Find customers owning a specific account ID"),
    Tool(name="get_accounts_by_customer", func=lambda x: str(get_accounts_by_customer(x)), description="Find accounts of cusomer by specific their username"),

    Tool(name="GetCustomerTiers", func=lambda x: str(get_customer_tiers()), description="Lists tier and benefit information of all customers"),
    Tool(name="GetCustomersByBirthYear", func=lambda x: str(get_customers_by_birth_year(int(x))), description="Get customers born in a specific year"),
    Tool(
        name="GetAccountsByNameOrUsername",
        func=lambda name: str(get_accounts_by_person_name_or_username(name)),
        description="Returns a list of account IDs for a customer using their name or username."
    ),
    #Transaction tools :-
    
    Tool(
        name="getTransactionsByAccount",
        func=lambda account_id, start_date=None, end_date=None: get_transactions_by_account(int(account_id), start_date, end_date),
        description="Retrieve all transactions for a specific account, optionally filtered by start_date and/or end_date in YYYY-MM-DD format"
    ),
    Tool(
        name="getTransactionSummaryByType",
        func=lambda account_id: get_transaction_summary_by_type(int(account_id)),
        description="Summarize the total number and value of each transaction type (e.g. buy, sell) for a given account"
    ),
    Tool(
        name="getTransactionsBySymbol",
        func=lambda account_id, symbol: get_transactions_by_symbol(int(account_id), symbol),
        description="Get all transactions involving a specific stock or currency symbol for a given account"
    ),
    Tool(
        name="getTransactionVolumeOverTime",
        func=lambda account_id, group_by="month": get_transaction_volume_over_time(int(account_id), group_by),
        description="Aggregate transaction count and total value over time (grouped by month or year) for a given account"
    ),
    Tool(
    name="FallbackHandler",
    func=lambda x: "I'm sorry, I couldn't find answer of your query. Try asking other question related to accounts, transactions, or customers.",
    description="Used when no other tools match or the input seems irrelevant"
)
]


# Step 5: Setup FAISS Vector Store for Semantic Similarity
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

# sample_questions = []
import json

with open("sample_questions.json") as f:
    questions_json = json.load(f)

sample_questions = questions_json["sample_questions"]


documents = [Document(page_content=q) for q in sample_questions]
vectorstore = FAISS.from_documents(documents, embedding_model)

# Step 6: Set up Conversational Agent
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType, initialize_agent
from langchain.agents.agent import AgentExecutor
from langchain.agents import Tool as LangchainTool

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

memory = ConversationBufferMemory(memory_key="chat_history")

# Wrap tools as LangchainTool for multi-step agent reasoning
wrapped_tools = [
    LangchainTool(name=tool.name, func=tool.func, description=tool.description)
    for tool in query_tools
]

agent = initialize_agent(
    tools=wrapped_tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True  # Helps in chaining multiple tool invocations
)

# Step 7: Run Example
if __name__ == "__main__":
    print("\nWelcome to the Conversational DB Agent!")
    print("Type your question (type 'exit' to quit):\n")
    while True:
        user_query = input("You: ")
        if user_query.lower() in ["exit", "quit"]:
            break

        # Use FAISS to find most similar known semantic intent*****
        try:
            similar_docs = vectorstore.similarity_search(user_query, k=1)
            if similar_docs:
                print("\n🔍 Closest matched intent:", similar_docs[0].page_content)
            else:
                print("\n🔍 No close match found. Attempting interpretation anyway...")
        except Exception as e:
            print("\n⚠️ Could not determine closest intent:", str(e))


        # Forward query to agent for execution
        try:
            response = agent.run(user_query)
            print("🤖 Agent:", response)
        except Exception as e:
            print("❌ Agent error:", str(e))
            print("🤖 Agent: Sorry, I couldn’t understand your query or it may be invalid. Try rephrasing or asking something else.")

"""
README NOTE:
This chatbot:
- Maps natural language to definitions, filters, aggregations, comparisons, and trend queries.
- Executes appropriate MongoDB queries and returns results.
- Falls back to semantic similarity matching (FAISS) to understand intent.
- Handles multi-turn conversations using LangChain memory.
- Supports multiple tool invocations per user query for complex reasoning.
"""
