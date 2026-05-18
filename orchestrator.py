from typing import TypedDict, Optional
from agents.jd_analyzer import jd_analyze
from agents.resume_parser import parse_resume
from agents.rewriter import rewrite_resume
from agents.reviewer import review
from agents.skill_matcher import match_skills

from langgraph.graph import StateGraph, END


# STATES
class ResumeState(TypedDict):
  #inputs
  resume_file: any
  jd_text: str

  #agent output
  resume_data: Optional[dict]
  jd_data: Optional[dict]
  match_data: Optional[dict]
  rewritten_data: Optional[dict]
  review_data: Optional[dict]

  #control
  retry_count: int
  approved: bool
  final_output: Optional[dict]

# NODES
def start_node(state: ResumeState) -> dict:
  return {}

def jd_analyzer_node(state: ResumeState) -> dict:
  #read jd
  jd_text = state['jd_text']
  print("Parsing Job Description...")
  jd_data = jd_analyze(jd_text)

  return {
    "jd_data": jd_data
  }

def parse_resume_node(state: ResumeState) -> dict:
  resume_file = state['resume_file']

  print("Parsing Resume...")
  resume_data = parse_resume(resume_file)

  return {
    "resume_data": resume_data
  }

def skills_matcher_node(state: ResumeState) -> dict:
    print("Matching Skills...")
    match_data = match_skills(
        state["jd_data"],
        state["resume_data"]
    )
    return {"match_data": match_data}

def rewrite_resume_node(state: ResumeState) -> dict:

  print("Rewriting Summary...")
  rewritten_data = rewrite_resume(
    state['resume_data'],
    state['jd_data'],
    state['match_data']
  )

  return {
    "rewritten_data": rewritten_data
  }

def review_scores_node(state: ResumeState) -> dict:
  print("Matching Skills...")
  review_data = review(
      state["rewritten_data"],
      state["jd_data"],
      state["match_data"]
  )
  return {
    "review_data": review_data,
    "approved": review_data["approved"],
    "retry_count": state["retry_count"] + 1
    }

#Pipeline's final return
def final_output_node(state: ResumeState) -> dict:
    print("Pipeline complete!")
    return {
        "final_output": {
            "rewritten": state["rewritten_data"],
            "review": state["review_data"],
            "match": state["match_data"]
        }
    }


#add router
def should_retry(state: ResumeState) -> str:
    approved = state["approved"]
    retry_count = state["retry_count"]

    if approved:
        print("Approved! Moving to final output.")
        return "approved"
    elif retry_count >= 2:
        print("Max retries reached. Moving to final output anyway.")
        return "max_retries_reached"
    else:
        print(f"Not approved. Retrying... (attempt {retry_count})")
        return "retry"


#graph assemeble
def build_graph():
   graph = StateGraph(ResumeState)

   #add all nodes
   graph.add_node("start_node", start_node)
   graph.add_node("jd_analyzer_node", jd_analyzer_node)
   graph.add_node("parse_resume_node", parse_resume_node)
   graph.add_node("skills_matcher_node", skills_matcher_node)
   graph.add_node("rewrite_resume_node", rewrite_resume_node)
   graph.add_node("review_scores_node", review_scores_node)
   graph.add_node("final_output_node", final_output_node)

   #condition
   graph.set_entry_point("start_node")

   #normal edges
   graph.add_edge("start_node", "jd_analyzer_node")
   graph.add_edge("start_node", "parse_resume_node")
   graph.add_edge("jd_analyzer_node", "skills_matcher_node")
   graph.add_edge("parse_resume_node", "skills_matcher_node")
   graph.add_edge("skills_matcher_node", "rewrite_resume_node")
   graph.add_edge("rewrite_resume_node", "review_scores_node")
   graph.add_edge("final_output_node", END)

   #conditional edges
   graph.add_conditional_edges(
      "review_scores_node",
      should_retry,
      {
         "approved": "final_output_node",
         "max_retries_reached": "final_output_node",
         "retry": "rewrite_resume_node"
      }
   )

   return graph.compile()

#pipeline entry point
def run_pipeline(resume_file, jd_text: str, status_callback=None):
   app = build_graph()

   initial_state = {
    "resume_file": resume_file,
    "jd_text": jd_text,
    "jd_data": None,
    "resume_data": None,
    "match_data": None,
    "rewritten_data": None,
    "review_data": None,
    "retry_count": 0,
    "approved": False,
    "final_output": None
    }
   
  # map node name → display message
   node_messages = {
        "jd_analyzer_node":    "🔍 Analyzing job description...",
        "parse_resume_node":   "📄 Parsing resume...",
        "skills_matcher_node": "🎯 Matching skills...",
        "rewrite_resume_node": "✍️  Rewriting resume sections...",
        "review_scores_node":  "✅ Reviewing quality...",
        "final_output_node":   "📦 Assembling final output...",
    }

   final_output = None

   for update in app.stream(initial_state):
        node_name = list(update.keys())[0]

        # i-call ang callback kung may nakalagay
        if status_callback and node_name in node_messages:
            status_callback(node_messages[node_name])

        if "final_output_node" in update:
            final_output = update["final_output_node"]["final_output"]

   return final_output
