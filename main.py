import streamlit as st
import openai
import json

# -----------------------------
# Synthetic Data (same as before)
# -----------------------------
BILLS = [
    {
        "bill_id": 1,
        "session_year": 2025,
        "bill_number": "HB 1001",
        "title": "Education Funding Enhancement",
        "summary": "This bill aims to increase the budget for K-12 education in Indiana by adjusting local property tax revenue distributions.",
        "status": "Passed House",
        "last_action_date": "2025-02-10",
        "last_action_text": "Referred to Senate Committee on Education",
        "chamber": "House",
        "source": "https://iga.in.gov/legislation/2025/hb1001",
    },
    {
        "bill_id": 2,
        "session_year": 2025,
        "bill_number": "HB 1221",
        "title": "Transportation Infrastructure Program",
        "summary": "A bill to improve state highways and local roads through targeted funding and a new oversight commission.",
        "status": "Introduced",
        "last_action_date": "2025-01-15",
        "last_action_text": "Filed and referred to House Committee on Transportation",
        "chamber": "House",
        "source": "https://iga.in.gov/legislation/2025/hb1221",
    },
    {
        "bill_id": 3,
        "session_year": 2025,
        "bill_number": "SB 373",
        "title": "Healthcare Price Transparency",
        "summary": "Requires hospitals to publish standard charges for procedures and provides mechanisms for enforcement by the state.",
        "status": "In Committee",
        "last_action_date": "2025-01-20",
        "last_action_text": "Referred to Senate Committee on Health and Provider Services",
        "chamber": "Senate",
        "source": "https://iga.in.gov/legislation/2025/sb373",
    },
    {
        "bill_id": 4,
        "session_year": 2025,
        "bill_number": "SB 400",
        "title": "Renewable Energy Incentives",
        "summary": "Provides tax incentives for solar and wind projects and establishes a green energy development task force.",
        "status": "Passed Senate",
        "last_action_date": "2025-03-01",
        "last_action_text": "Passed Senate with amendments, transmitted to House",
        "chamber": "Senate",
        "source": "https://iga.in.gov/legislation/2025/sb400",
    },
    {
        "bill_id": 5,
        "session_year": 2025,
        "bill_number": "HB 1390",
        "title": "Criminal Justice Reform",
        "summary": "Revises sentencing guidelines and expands reentry programs for nonviolent offenders.",
        "status": "Enrolled",
        "last_action_date": "2025-03-15",
        "last_action_text": "Enrolled, awaiting Governor's signature",
        "chamber": "House",
        "source": "https://iga.in.gov/legislation/2025/hb1390",
    },
]

SPONSORS = [
    {"sponsor_id": 1, "name": "Alice Johnson", "party": "R", "chamber": "House"},
    {"sponsor_id": 2, "name": "Bob Smith",    "party": "D", "chamber": "House"},
    {"sponsor_id": 3, "name": "Carlos Martinez", "party": "R", "chamber": "Senate"},
    {"sponsor_id": 4, "name": "Diana Chang",  "party": "D", "chamber": "House"},
    {"sponsor_id": 5, "name": "Emily Davis",  "party": "R", "chamber": "Senate"},
    {"sponsor_id": 6, "name": "Frank Thomas", "party": "D", "chamber": "Senate"},
]

BILL_SPONSORS = [
    {"bill_id": 1, "sponsor_id": 1, "role": "Primary"},
    {"bill_id": 1, "sponsor_id": 2, "role": "Co-sponsor"},
    {"bill_id": 2, "sponsor_id": 2, "role": "Primary"},
    {"bill_id": 2, "sponsor_id": 4, "role": "Co-sponsor"},
    {"bill_id": 3, "sponsor_id": 3, "role": "Primary"},
    {"bill_id": 3, "sponsor_id": 6, "role": "Co-sponsor"},
    {"bill_id": 4, "sponsor_id": 5, "role": "Primary"},
    {"bill_id": 5, "sponsor_id": 1, "role": "Primary"},
    {"bill_id": 5, "sponsor_id": 3, "role": "Co-sponsor"},
]

ACTIONS = [
    {"action_id": 1,  "bill_id": 1, "date": "2025-01-05", "chamber": "House",  "description": "Introduced in House"},
    {"action_id": 2,  "bill_id": 1, "date": "2025-01-10", "chamber": "House",  "description": "Passed House on third reading"},
    {"action_id": 3,  "bill_id": 1, "date": "2025-02-10", "chamber": "House",  "description": "Referred to Senate Committee on Education"},

    {"action_id": 4,  "bill_id": 2, "date": "2025-01-15", "chamber": "House",  "description": "Filed and referred to House Committee on Transportation"},

    {"action_id": 5,  "bill_id": 3, "date": "2025-01-12", "chamber": "Senate", "description": "Introduced in Senate"},
    {"action_id": 6,  "bill_id": 3, "date": "2025-01-20", "chamber": "Senate", "description": "Referred to Senate Committee on Health and Provider Services"},

    {"action_id": 7,  "bill_id": 4, "date": "2025-02-10", "chamber": "Senate", "description": "Introduced in Senate"},
    {"action_id": 8,  "bill_id": 4, "date": "2025-02-20", "chamber": "Senate", "description": "Passed Senate with amendments"},
    {"action_id": 9,  "bill_id": 4, "date": "2025-03-01", "chamber": "Senate", "description": "Transmitted to House"},

    {"action_id": 10, "bill_id": 5, "date": "2025-01-15", "chamber": "House",  "description": "Introduced in House"},
    {"action_id": 11, "bill_id": 5, "date": "2025-02-20", "chamber": "House",  "description": "Passed House on third reading"},
    {"action_id": 12, "bill_id": 5, "date": "2025-03-15", "chamber": "House",  "description": "Enrolled, awaiting Governor's signature"},
]

# -----------------------------
# Helper functions to query data
# -----------------------------
def get_bill_details(bill_number: str):
    """
    Return info about a single bill, including summary, status, sponsors, and actions.
    """
    bill = next((b for b in BILLS if b["bill_number"].lower() == bill_number.lower()), None)
    if not bill:
        return {"error": f"No bill found with number {bill_number}"}

    # gather sponsors
    sponsor_links = [bs for bs in BILL_SPONSORS if bs["bill_id"] == bill["bill_id"]]
    sponsor_info = []
    for link in sponsor_links:
        sponsor = next((s for s in SPONSORS if s["sponsor_id"] == link["sponsor_id"]), None)
        if sponsor:
            sponsor_info.append({
                "name": sponsor["name"],
                "party": sponsor["party"],
                "chamber": sponsor["chamber"],
                "role": link["role"]
            })

    # gather actions
    action_records = [a for a in ACTIONS if a["bill_id"] == bill["bill_id"]]
    action_records_sorted = sorted(action_records, key=lambda x: x["date"])

    return {
        "bill_number": bill["bill_number"],
        "title": bill["title"],
        "summary": bill["summary"],
        "status": bill["status"],
        "last_action_date": bill["last_action_date"],
        "last_action_text": bill["last_action_text"],
        "chamber": bill["chamber"],
        "session_year": bill["session_year"],
        "source": bill["source"],
        "sponsors": sponsor_info,
        "actions": action_records_sorted
    }

def search_bills(query: str):
    """
    Simple search that returns bills whose title/summary/bill_number contain the query text.
    """
    query_lower = query.lower()
    matches = []
    for b in BILLS:
        combined_text = f"{b['bill_number']} {b['title']} {b['summary']}".lower()
        if query_lower in combined_text:
            matches.append(b["bill_number"])
    return {"matches": matches}

# -------------------------------------
# OpenAI function definitions (JSON)
# -------------------------------------
def get_openai_functions():
    return [
        {
            "name": "get_bill_details",
            "description": "Get details for a given bill, including summary, status, sponsors, and actions",
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_number": {
                        "type": "string",
                        "description": "Bill number, e.g. 'HB 1001' or 'SB 373'"
                    }
                },
                "required": ["bill_number"]
            },
        },
        {
            "name": "search_bills",
            "description": "Search for bills by matching a keyword or phrase in their bill number, title, or summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term to match."
                    }
                },
                "required": ["query"]
            },
        },
    ]

def call_function_by_name(function_name, arguments):
    if function_name == "get_bill_details":
        return get_bill_details(**arguments)
    elif function_name == "search_bills":
        return search_bills(**arguments)
    else:
        return {"error": f"Unknown function: {function_name}"}

# -------------------------------------
# Streamlit Chat App
# -------------------------------------
def main():
    st.title("Indiana Legislation Chatbot (MVP)")

    # openai.api_key
    openai.api_key = ''

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that provides information about Indiana bills. "
                    "You can call the following functions to retrieve real data about bills, or search for them. "
                    "If the user asks about a specific bill, call get_bill_details. "
                    "If they want to find bills by a keyword, call search_bills. "
                    
                    "Only use the function results to answer. "
                )
            }
        ]

    user_input = st.text_input("Ask about Indiana bills (e.g. 'What is HB 1221 about?'):")
    if st.button("Send") and user_input.strip():
        st.session_state["messages"].append({"role": "user", "content": user_input})

        response = openai.chat.completions.create(
            model="gpt-4.1",  # or "gpt-4-0613"
            messages=st.session_state["messages"],
            functions=get_openai_functions(),
            function_call="auto"  # let the model decide
        )

        msg = response.choices[0].message  # This is the top-level message
        if msg.function_call:
            # The model wants to call a function
            function_name = msg.function_call.name
            function_args = msg.function_call.arguments

            # Parse arguments (they come as a string, so we load JSON)
            try:
                args_dict = json.loads(function_args)
            except:
                args_dict = {}

            # Actually call the function
            function_result = call_function_by_name(function_name, args_dict)

            # Add the function call + result to messages
            st.session_state["messages"].append({
                "role": "assistant",
                "name": function_name,
                "content": function_args
            })
            st.session_state["messages"].append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_result)
            })

            # Now get the final answer from the model with the function result
            second_response = openai.chat.completions.create(
                model="gpt-4.1",
                messages=st.session_state["messages"],
            )
            final_msg = second_response.choices[0].message
            st.session_state["messages"].append({"role": "assistant", "content": final_msg.content})

            #st.write(final_msg.content)
            # I was thinking about just adding system prompt to ask ai to add source link at the end, turns out not consistent, 
            # so I change mind and just attached retrieved link at the end of ai's response
            

            
            # DISPLAY:
            st.markdown(final_msg.content)   # show GPT’s answer
            if function_name == "get_bill_details":
            # function_result["source"] holds the URL
                st.markdown(f"[🔗 Read the full bill here]({function_result['source']})")
        else:
            # No function call, just a direct answer
            st.session_state["messages"].append({"role": "assistant", "content": msg.content})
            st.write(msg.content)



    # For debugging, show every step
    #for i, chat_msg in enumerate(st.session_state["messages"]):
    #    role = chat_msg["role"]
    #    if role == "user":
    #        st.markdown(f"**User:** {chat_msg['content']}")
    #    elif role == "assistant":
    #        if "name" in chat_msg:
    #            st.markdown(f"**Assistant (function call):** {chat_msg['name']} args = {chat_msg['content']}")
    #        else:
    #            st.markdown(f"**Assistant:** {chat_msg['content']}")
    #    elif role == "function":
    #        st.markdown(f"*Function '{chat_msg['name']}' result:* `{chat_msg['content']}`")
    #    elif role == "system":
    #        # Typically we don't display the system prompt to end-users
    #        pass

if __name__ == "__main__":
    main()
