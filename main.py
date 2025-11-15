import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Page config
st.set_page_config(
    page_title="Prompt Engineering Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design with specified color palette
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #0288D1; /* Professional Blue */
        --dark: #263238;    /* Blue-Grey Charcoal */
        --light: #E1F5FE;   /* Very Light Blue */
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%);
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0288D1 0%, #01579B 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(2, 136, 209, 0.3);
    }
    
    .main-header h1 {
        color: white; /* Changed to white for better contrast on blue */
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: white;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Chat messages */
    .user-message {
        background: #263238;
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #0288D1;
    }
    
    .assistant-message {
        background: white;
        color: #333333;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #0288D1;
    }
    
    .thinking-box {
        background: #E1F5FE;
        border: 2px dashed #0288D1;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-style: italic;
        color: #263238;
    }
    
    .question-box {
        background: linear-gradient(135deg, #0288D1 0%, #0277BD 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(2, 136, 209, 0.3);
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0288D1 0%, #0277BD 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(2, 136, 209, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(2, 136, 209, 0.4);
    }
    
    /* Input fields (Corrected) */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid #FFA726;
        border-radius: 10px;
        padding: 0.75rem;
        background: white;
        color: #333333;
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #263238 0%, #37474F 100%);
    }
    
    .css-1d391kg p, [data-testid="stSidebar"] p,
    .css-1d391kg label, [data-testid="stSidebar"] label {
        color: #E1F5FE !important;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
    
    .badge-thinking {
        background: #0288D1;
        color: white;
    }
    
    .badge-questioning {
        background: #039BE5;
        color: white;
    }
    
    .badge-ready {
        background: #00C853;
        color: white;
    }
    
    /* FIX FOR WIDGET LABELS */
    [data-testid="stAppViewContainer"] label {
        color: #333333;
        font-weight: 600;
    }

    /* FIX FOR PLACEHOLDER TEXT */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #888888;
    }
    
    /* Streaming cursor effect */
    .streaming-cursor {
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'phase' not in st.session_state:
    st.session_state.phase = 'initial'  # initial, questioning, refining
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'original_prompt' not in st.session_state:
    st.session_state.original_prompt = ""

# Header
st.markdown("""
<div class="main-header">
    <h1>🎯 Prompt Engineering Assistant</h1>
    <p>Let's craft the perfect prompt together through intelligent questioning</p>
</div>
""", unsafe_allow_html=True)

api_key = os.getenv("GEMINI_API_KEY")

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.markdown(f"**Questions Asked:** {st.session_state.question_count}")
    st.markdown(f"**Phase:** {st.session_state.phase.title()}")
    
    if st.session_state.phase == 'initial':
        st.markdown('<span class="status-badge badge-ready">Ready to Start</span>', unsafe_allow_html=True)
    elif st.session_state.phase == 'questioning':
        st.markdown('<span class="status-badge badge-questioning">In Discussion</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge badge-thinking">Refining</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.phase = 'initial'
        st.session_state.question_count = 0
        st.session_state.original_prompt = ""
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 How it works")
    st.markdown("""
    1. **Share your prompt idea**
    2. **Answer engaging questions** to refine it
    3. **Get an optimized prompt** with reasoning
    """)

# Initialize OpenAI client with Gemini
def get_client(api_key):
    return OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

# System prompt for the CoT model
SYSTEM_PROMPT = SYSTEM_PROMPT = """You are an elite prompt engineering specialist utilizing advanced chain-of-thought methodologies to optimize user prompts through systematic elicitation and iterative refinement.

Core Methodology:
1. Initial Analysis: Conduct comprehensive domain-specific analysis of the user's prompt, evaluating semantic clarity, contextual boundaries, and intended output parameters
2. Gap Identification: Systematically identify ambiguities, missing constraints, undefined success metrics, and opportunities for specification enhancement
3. Strategic Elicitation: Formulate ONE targeted, high-impact question designed to extract critical information that will materially improve prompt effectiveness
4. Iterative Refinement: After each response, perform meta-cognitive analysis (explicitly documented in <THINKING> tags) and generate the next strategic question
5. Convergence Point: After 3-5 strategic inquiries, synthesize all gathered insights and deliver an architecturally sound, production-ready prompt with comprehensive technical rationale

Question Design Principles:
- Precision-Oriented: Target specific ambiguities, undefined parameters, or missing constraints
- Actionable Focus: Elicit information that directly improves prompt structure, output specifications, or constraint definitions
- Cognitive Engagement: Frame questions to stimulate critical thinking about implementation details, edge cases, scalability requirements, and measurable success criteria
- Professional Tone: Maintain technical rigor while demonstrating genuine investment in achieving the user's objectives
- Motivational Framing: Position each inquiry as a stepping stone toward building a robust, production-grade solution

Response Structure Protocol:
- Analysis Phase: Begin with <THINKING> tags containing your expert chain-of-thought reasoning, technical assessment, and strategic rationale
- Elicitation Phase: Present ONE clear, professionally-framed question that advances prompt optimization
- Synthesis Phase: After sufficient iterations (typically 3-5), deliver the enhanced prompt with detailed technical justification, including: architectural decisions, constraint definitions, output specifications, and quality assurance considerations

Your objective: Transform initial prompt concepts into technically precise, contextually rich, and operationally effective prompts that maximize output quality and reliability. Ensure the user feels empowered and strategically guided throughout the refinement process."""

def stream_gemini(client, messages):
    """Stream Gemini API responses"""
    try:
        stream = client.chat.completions.create(
            model="gemini-2.5-flash-lite",
            messages=messages,
            temperature=0.8,
            max_tokens=2000,
            stream=True
        )
        return stream
    except Exception as e:
        return None

def parse_streaming_content(content):
    """Parse content to separate thinking and question parts"""
    if '<THINKING>' in content and '</THINKING>' in content:
        thinking_start = content.find('<THINKING>') + len('<THINKING>')
        thinking_end = content.find('</THINKING>')
        thinking = content[thinking_start:thinking_end].strip()
        question = content[thinking_end + len('</THINKING>'):].strip()
        return thinking, question, True
    return None, content, False

# Display conversation history
for msg in st.session_state.conversation_history:
    if msg['role'] == 'user':
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 You:</strong><br>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)
    else:
        content = msg['content']
        thinking, question, has_thinking = parse_streaming_content(content)
        
        if has_thinking:
            st.markdown(f"""
            <div class="assistant-message">
                <strong>🤖 Assistant:</strong><br>
                <div class="thinking-box">
                    💭 <strong>Thinking:</strong> {thinking}
                </div>
                <div class="question-box">
                    ❓ {question}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <strong>🤖 Assistant:</strong><br>
                {content.replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)

# Main input area
st.markdown("---")

col1, col2 = st.columns([4, 1])

with col1:
    if st.session_state.phase == 'initial':
        user_input = st.text_area(
            "What prompt would you like to engineer?",
            placeholder="E.g., I want to create a prompt for generating creative blog post ideas about technology...",
            height=100,
            key="initial_input"
        )
    else:
        user_input = st.text_area(
            "Your answer:",
            placeholder="Share your thoughts here...",
            height=100,
            key="answer_input"
        )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.button("🚀 Send", use_container_width=True, type="primary")

# Process input with streaming
if submit_button and user_input and api_key:
    # Add user message
    st.session_state.conversation_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Store original prompt if this is the first message
    if st.session_state.phase == 'initial':
        st.session_state.original_prompt = user_input
        st.session_state.phase = 'questioning'
    
    # Prepare messages for API
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT}
    ] + st.session_state.conversation_history
    
    # Create placeholders for streaming
    assistant_container = st.container()
    
    with assistant_container:
        st.markdown('<div class="assistant-message"><strong>🤖 Assistant:</strong><br>', unsafe_allow_html=True)
        thinking_placeholder = st.empty()
        question_placeholder = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Get streaming response
    client = get_client(api_key)
    stream = stream_gemini(client, messages)
    
    if stream:
        full_response = ""
        thinking_text = ""
        question_text = ""
        in_thinking = False
        thinking_complete = False
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                
                # Parse streaming content
                if '<THINKING>' in full_response and not in_thinking:
                    in_thinking = True
                
                if in_thinking and not thinking_complete:
                    if '</THINKING>' in full_response:
                        thinking_complete = True
                        # Extract thinking content
                        thinking_start = full_response.find('<THINKING>') + len('<THINKING>')
                        thinking_end = full_response.find('</THINKING>')
                        thinking_text = full_response[thinking_start:thinking_end].strip()
                        question_text = full_response[thinking_end + len('</THINKING>'):].strip()
                        
                        # Display thinking
                        thinking_placeholder.markdown(f"""
                        <div class="thinking-box">
                            💭 <strong>Thinking:</strong> {thinking_text}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Still collecting thinking
                        if '<THINKING>' in full_response:
                            thinking_start = full_response.find('<THINKING>') + len('<THINKING>')
                            thinking_text = full_response[thinking_start:].strip()
                            thinking_placeholder.markdown(f"""
                            <div class="thinking-box">
                                💭 <strong>Thinking:</strong> {thinking_text}<span class="streaming-cursor">▌</span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    # Update question as it streams
                    if thinking_complete:
                        thinking_start = full_response.find('<THINKING>') + len('<THINKING>')
                        thinking_end = full_response.find('</THINKING>')
                        question_text = full_response[thinking_end + len('</THINKING>'):].strip()
                        
                        question_placeholder.markdown(f"""
                        <div class="question-box">
                            ❓ {question_text}<span class="streaming-cursor">▌</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # No thinking tags, just stream as question
                        question_placeholder.markdown(f"""
                        <div style="color: #333333;">
                            {full_response}<span class="streaming-cursor">▌</span>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Final update without cursor
        if thinking_complete:
            question_placeholder.markdown(f"""
            <div class="question-box">
                ❓ {question_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            question_placeholder.markdown(f"""
            <div style="color: #333333;">
                {full_response}
            </div>
            """, unsafe_allow_html=True)
        
        # Add assistant response to history
        st.session_state.conversation_history.append({
            'role': 'assistant',
            'content': full_response
        })
        
        # Update question count
        st.session_state.question_count += 1
        
        # Check if we should move to refining phase
        if st.session_state.question_count >= 3 and 'enhanced prompt' in full_response.lower():
            st.session_state.phase = 'refining'
        
        st.rerun()
    else:
        st.error("⚠️ Error connecting to Gemini API. Please check your API key.")

elif submit_button and not api_key:
    st.error("⚠️ Please enter your Gemini API key in the sidebar!")
elif submit_button and not user_input:
    st.warning("⚠️ Please enter your prompt or answer!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #333333; padding: 1rem;">
    <p>Optimized to help you craft better prompts</p>
</div>
""", unsafe_allow_html=True)