# 4.The Specialist Agents (Upgraded for Production)
#4.The Specialist Agents (Fully Upgraded with Full Dependency Injection)
# -------------------------------------------------------------------------
# We now complete the upgrade of our specialist agents.
# The final step is to pass the configuration variables (like model names
# AND namespaces) as arguments, making the agents fully self-contained and
# removing all reliance on global variables.
# -------------------------------------------------------------------------

# === 4.1. Context Librarian Agent (Upgraded) ===
# *** Added 'namespace_context' argument ***
def agent_context_librarian(mcp_message, client, index, embedding_model, namespace_context):
    """
    Retrieves the appropriate Semantic Blueprint from the Context Library.
    UPGRADE: Now also accepts embedding_model and namespace configuration.
    """
    logging.info("[Librarian] Activated. Analyzing intent...")
    try:
        requested_intent = mcp_message['content'].get('intent_query')

        if not requested_intent:
            raise ValueError("Librarian requires 'intent_query' in the input content.")

        # UPGRADE: Pass all necessary dependencies to the hardened helper function.
        results = query_pinecone(
            query_text=requested_intent,
            # *** Use the passed argument instead of the global variable ***
            namespace=namespace_context,
            top_k=1,
            index=index,
            client=client,
            embedding_model=embedding_model
        )

        if results:
            match = results[0]
            logging.info(f"[Librarian] Found blueprint '{match['id']}' (Score: {match['score']:.2f})")
            blueprint_json = match['metadata']['blueprint_json']
            content = blueprint_json
        else:
            logging.warning("[Librarian] No specific blueprint found. Returning default.")
            content = json.dumps({"instruction": "Generate the content neutrally."})

        return create_mcp_message("Librarian", content)

    except Exception as e:
        logging.error(f"[Librarian] An error occurred: {e}")
        raise e

# === 4.2. Researcher Agent (Upgraded) ===
# *** 'namespace_knowledge' argument ***
def agent_researcher(mcp_message, client, index, generation_model, embedding_model, namespace_knowledge):
    """
    Retrieves and synthesizes factual information from the Knowledge Base.
    UPGRADE: Now accepts all necessary model and namespace configurations.
    """
    logging.info("[Researcher] Activated. Investigating topic...")
    try:
        topic = mcp_message['content'].get('topic_query')

        if not topic:
            raise ValueError("Researcher requires 'topic_query' in the input content.")

        # UPGRADE: Pass all dependencies to the Pinecone helper.
        results = query_pinecone(
            query_text=topic,
            # *** Use the passed argument instead of the global variable ***
            namespace=namespace_knowledge,
            top_k=3,
            index=index,
            client=client,
            embedding_model=embedding_model
        )

        if not results:
            logging.warning("[Researcher] No relevant information found.")
            return create_mcp_message("Researcher", "No data found on the topic.")

        logging.info(f"[Researcher] Found {len(results)} relevant chunks. Synthesizing...")
        source_texts = [match['metadata']['text'] for match in results]

        system_prompt = """You are an expert research synthesis AI.
        Synthesize the provided source texts into a concise, bullet-pointed summary relevant to the user's topic. Focus strictly on the facts provided in the sources. Do not add outside information."""

        user_prompt = f"Topic: {topic}\n\nSources:\n" + "\n\n---\n\n".join(source_texts)

        # UPGRADE: Pass all dependencies to the LLM helper.
        findings = call_llm_robust(
            system_prompt,
            user_prompt,
            client=client,
            generation_model=generation_model
        )

        return create_mcp_message("Researcher", findings)

    except Exception as e:
        logging.error(f"[Researcher] An error occurred: {e}")
        raise e

# === 4.3. Writer Agent (Upgraded) ===
def agent_writer(mcp_message, client, generation_model):
    """
    Combines research with a blueprint to generate the final output.
    UPGRADE: Now accepts the generation_model configuration.
    """
    logging.info("[Writer] Activated. Applying blueprint to source material...")
    try:
        blueprint_json_string = mcp_message['content'].get('blueprint')
        facts = mcp_message['content'].get('facts')
        previous_content = mcp_message['content'].get('previous_content')

        if not blueprint_json_string:
            raise ValueError("Writer requires 'blueprint' in the input content.")

        if facts:
            source_material = facts
            source_label = "RESEARCH FINDINGS"
        elif previous_content:
            source_material = previous_content
            source_label = "PREVIOUS CONTENT (For Rewriting)"
        else:
            raise ValueError("Writer requires either 'facts' or 'previous_content'.")

        system_prompt = f"""You are an expert content generation AI.
        Your task is to generate content based on the provided SOURCE MATERIAL.
        Crucially, you MUST structure, style, and constrain your output according to the rules defined in the SEMANTIC BLUEPRINT provided below.

        --- SEMANTIC BLUEPRINT (JSON) ---
        {blueprint_json_string}
        --- END SEMANTIC BLUEPRINT ---

        Adhere strictly to the blueprint's instructions, style guides, and goals. The blueprint defines HOW you write; the source material defines WHAT you write about.
        """

        user_prompt = f"""
        --- SOURCE MATERIAL ({source_label}) ---
        {source_material}
        --- END SOURCE MATERIAL ---

        Generate the content now, following the blueprint precisely.
        """

        # UPGRADE: Pass all dependencies to the robust LLM call.
        final_output = call_llm_robust(
            system_prompt,
            user_prompt,
            client=client,
            generation_model=generation_model
        )

        return create_mcp_message("Writer", final_output)

    except Exception as e:
        logging.error(f"[Writer] An error occurred: {e}")
        raise e

logging.info("✅ Specialist Agents defined and fully upgraded.")
