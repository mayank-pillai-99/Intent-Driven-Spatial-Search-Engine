import nbformat
import json

notebook_path = "notebooks/Final.ipynb"
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

# We will iterate over code cells and replace/inject strings.
for cell in nb.cells:
    if cell.cell_type == "code":
        source = cell.source
        
        # 1. Add imports and process_pdf function
        if "from langchain_community.document_loaders import PyPDFLoader" not in source and "import gradio as gr" in source:
            injection = """
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

rag_vector_db = None
rag_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_pdf(filepath):
    global rag_vector_db
    if filepath is None: return "No file uploaded."
    try:
        loader = PyPDFLoader(filepath)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        rag_vector_db = FAISS.from_documents(splits, rag_embeddings)
        return f"✅ PDF processed! Loaded {len(splits)} chunks into RAG memory."
    except Exception as e:
        return f"❌ Error processing PDF: {str(e)}"
"""
            cell.source = source.replace("import gradio as gr", injection + "\nimport gradio as gr")

        # 2. Update route_question and add generate_rag_response
        if "def route_question(question):" in source:
            # Replace the intent classification prompt
            old_prompt = "\"You are an intent classifier. Output DB if the user is asking for places, food, amenities, or locations (even implicitly like 'I am hungry' or 'I need something cheap'). Output CHAT ONLY for pure small talk (e.g., 'Hello', 'Who are you?', 'Write a poem','Write me code'). Only output DB or CHAT.\""
            new_prompt = "\"You are an intent classifier. Output DB if the user is asking for places, food, amenities, or locations. Output POLICY if the user is asking about rules, regulations, deadlines, fees, or curriculum. Output CHAT ONLY for pure small talk. Only output DB, POLICY, or CHAT.\""
            source = source.replace(old_prompt, new_prompt)
            
            # Inject generate_rag_response
            rag_response_func = """
def generate_rag_response(question, target_lang_code):
    if rag_vector_db is None:
        error_msg = "Please upload a college handbook PDF first so I can answer policy questions."
        return translate_english_to_target(error_msg, target_lang_code)
    
    docs = rag_vector_db.similarity_search(question, k=3)
    context = "\\n\\n".join([doc.page_content for doc in docs])
    
    prompt = f"Use the following rules/context to answer the user's question. If the answer is not in the context, say 'I cannot find the answer in the handbook.'\\n\\nContext:\\n{context}\\n\\nQuestion: {question}"
    
    messages = [
        {"role": "system", "content": "You are a helpful campus assistant answering rule/policy questions based on the provided handbook text."},
        {"role": "user", "content": prompt}
    ]
    
    formatted_prompt = sql_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = sql_tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    import torch
    with torch.no_grad():
        outputs = sql_model.generate(**inputs, max_new_tokens=250, do_sample=False)
    
    english_answer = sql_tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    return translate_english_to_target(english_answer, target_lang_code)

"""
            if "def generate_rag_response(" not in source:
                source = source.replace("def route_question(question):", rag_response_func + "\ndef route_question(question):")
            
            # Update chat_wrapper routing
            old_chat_routing = """    if "CHAT" in route_question(english_query):
        qwen_english_response = get_friendly_response(user_input, "Strictly tell the user that you are a map assistant and you can only help them find locations on campus. Refuse to answer their question.")
        # Translate it!
        final_localized_response = translate_english_to_target(qwen_english_response, target_lang_code)

        history.append([user_input, final_localized_response])
        return "", None, history, default_map, generate_audio_response(final_localized_response, target_lang_code)"""

            new_chat_routing = """    intent = route_question(english_query)
    if "CHAT" in intent:
        qwen_english_response = get_friendly_response(user_input, "Strictly tell the user that you are a campus assistant and can only help with map locations or college rules (if a PDF is uploaded). Refuse to answer general questions.")
        final_localized_response = translate_english_to_target(qwen_english_response, target_lang_code)
        history.append([user_input, final_localized_response])
        return "", None, history, default_map, generate_audio_response(final_localized_response, target_lang_code)
    
    elif "POLICY" in intent:
        final_localized_response = generate_rag_response(english_query, target_lang_code)
        history.append([user_input, final_localized_response])
        return "", None, history, default_map, generate_audio_response(final_localized_response, target_lang_code)"""
            
            source = source.replace(old_chat_routing, new_chat_routing)

            # Update UI
            ui_old = """        with gr.Row():
            college_input = gr.Textbox(label="Step 1: Enter College/City Name", placeholder="e.g., IIT Delhi", scale=3)
            btn_load = gr.Button("🌍 Map & Load Database", elem_classes="custom-button", size="lg", scale=1)
            btn_audit = gr.Button("📊 Audit Map Data", elem_classes="custom-button", size="lg", scale=1)

        status_box = gr.Textbox(label="System Status", interactive=False, value="✨ Ready! Map a college first.", elem_classes="status-box")
        btn_load.click(fn=load_college_data, inputs=college_input, outputs=status_box)
        btn_audit.click(fn=ui_audit_data, outputs=status_box)"""

            ui_new = """        with gr.Row():
            college_input = gr.Textbox(label="Step 1: Enter College/City Name", placeholder="e.g., IIT Delhi", scale=3)
            btn_load = gr.Button("🌍 Map & Load Database", elem_classes="custom-button", size="lg", scale=1)
            btn_audit = gr.Button("📊 Audit Map Data", elem_classes="custom-button", size="lg", scale=1)
            
        with gr.Row():
            pdf_upload = gr.File(label="Optional: Upload College Handbook (PDF) for Policy Q&A", file_types=[".pdf"])

        status_box = gr.Textbox(label="System Status", interactive=False, value="✨ Ready! Map a college first.", elem_classes="status-box")
        
        btn_load.click(fn=load_college_data, inputs=college_input, outputs=status_box)
        btn_audit.click(fn=ui_audit_data, outputs=status_box)
        pdf_upload.upload(fn=process_pdf, inputs=pdf_upload, outputs=status_box)"""

            source = source.replace(ui_old, ui_new)
            
            cell.source = source

with open(notebook_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Notebook updated successfully!")
