TAB3_STYLE = """
        <style>
        :root{
          --chat-bg: #fafafa;
          --border: #e6e6e6;
          --user-bg: #DCF8C6;
          --npc-bg: #ffffff;
          --text: #0b0b0b;
          --meta: #666666;
          --input-bg: #ffffff;
          --input-text: #0b0b0b;
        }

        /* Dark mode */
        @media (prefers-color-scheme: dark) {
          :root{
            --chat-bg: #0f1113;
            --border: #2b2b2b;
            --user-bg: #234f31;   /* ciemniejszy zielony dla balonika użytkownika */
            --npc-bg: #161617;    /* ciemne tło dla NPC */
            --text: #e6eef6;
            --meta: #9aa3b2;
            --input-bg: #0f1113;
            --input-text: #e6eef6;
          }
        }

        /* Chatbox and messages */
        .chatbox{
          height:420px;
          overflow:auto;
          padding:12px;
          border:1px solid var(--border);
          border-radius:8px;
          background:var(--chat-bg);
        }
        .msg{
          margin:8px 0;
          padding:10px;
          border-radius:12px;
          max-width:80%;
          display:block;
          clear:both;
          color:var(--text);
          word-wrap:break-word;
        }
        .msg.user{
          background:var(--user-bg);
          margin-left:auto;
          text-align:right;
        }
        .msg.npc{
          background:var(--npc-bg);
          margin-right:auto;
          text-align:left;
          border:1px solid var(--border);
        }
        .meta{
          font-size:12px;
          color:var(--meta);
          margin-bottom:6px;
        }

        /* Make Streamlit text inputs readable in dark mode */
        input[type="text"], textarea, .stTextInput > div > div > input {
          background: var(--input-bg) !important;
          color: var(--input-text) !important;
          border: 1px solid var(--border) !important;
          padding: 8px !important;
          border-radius: 6px !important;
        }
        input[type="text"]::placeholder, textarea::placeholder {
          color: var(--meta) !important;
        }

        /* small safety rules to keep contrast */
        .chatbox a { color: inherit; text-decoration: underline; }
        </style>
        <div class='chatbox'>
        """

TAB4_STYLE = """
<style>
:root {
    --chat-bg: #fafafa;
    --border: #e6e6e6;
    --npc1-bg: #DCF8C6;   /* zielony */
    --npc2-bg: #ffffff;   /* biały */
    --context-bg: #e0e0e0;
    --text: #0b0b0b;
    --meta: #666666;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    :root {
        --chat-bg: #0f1113;
        --border: #2b2b2b;
        --npc1-bg: #234f31;   /* ciemniejszy zielony */
        --npc2-bg: #161617;   /* ciemne szare */
        --context-bg: #2a2a2a;
        --text: #e6eef6;
        --meta: #9aa3b2;
    }
}

/* Chatbox and messages */
.chatbox {
    height: 420px;
    overflow: auto;
    padding: 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--chat-bg);
}

.msg {
    margin: 8px 0;
    padding: 10px;
    border-radius: 12px;
    max-width: 80%;
    display: block;
    clear: both;
    color: var(--text);
    word-wrap: break-word;
}

.msg.npc1 {
    background: var(--npc1-bg);
    margin-right: auto;
    text-align: left;
}

.msg.npc2 {
    background: var(--npc2-bg);
    margin-left: auto;
    text-align: right;
    border: 1px solid var(--border);
}

.msg.context {
    background: var(--context-bg);
    text-align: center;
    margin: 12px auto;
    max-width: 90%;
    font-style: italic;
}

.meta {
    font-size: 12px;
    color: var(--meta);
    margin-bottom: 6px;
}

/* Small safety rules to keep contrast */
.chatbox a {
    color: inherit;
    text-decoration: underline;
}
</style>
<div class='chatbox'>
"""
