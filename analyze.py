import os
import json
import anthropic
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def load_data():
    data = {}
    files = {
        'gsc_queries': 'data/gsc/queries.json',
        'gsc_pages':   'data/gsc/pages.json',
        'ga4_channels':'data/ga4/channels.json',
        'ga4_pages':   'data/ga4/pages.json',
    }
    for key, path in files.items():
        try:
            with open(path, 'r') as f:
                data[key] = json.load(f)
            print(f"Loaded: {path}")
        except:
            print(f"Missing: {path} - run python main.py first")
    return data

def ask_ai(question, data):
    print("\nAnalyzing your data...")
    print("-" * 50)

    context = f"""
You are an expert SEO analyst. Analyze this real website data for {os.getenv('GSC_PROPERTY_URL')} and answer clearly.

GOOGLE SEARCH CONSOLE DATA:
Top Queries: {json.dumps(data.get('gsc_queries', {}).get('queries', [])[:50], indent=2)}
Top Pages: {json.dumps(data.get('gsc_pages', {}).get('pages', [])[:50], indent=2)}

GOOGLE ANALYTICS 4 DATA:
Traffic by Channel: {json.dumps(data.get('ga4_channels', {}).get('channels', []), indent=2)}
Top Pages: {json.dumps(data.get('ga4_pages', {}).get('pages', [])[:50], indent=2)}

Data covers last 90 days.
Each query/page row has: keys[], clicks, impressions, ctr, position

QUESTION: {question}

Give a clear actionable answer with:
1. Direct answer with real numbers from data
2. Top 5 specific findings
3. Exact action items to take
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": context}]
    )
    return message.content[0].text

def save_report(question, answer):
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reports/analysis_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"SEO ANALYSIS REPORT\n")
        f.write(f"Site: {os.getenv('GSC_PROPERTY_URL')}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"QUESTION:\n{question}\n\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"ANALYSIS:\n{answer}\n")
    print(f"Report saved: {filename}")

def main():
    print("=" * 50)
    print("SEO AI ANALYSIS ENGINE")
    print("=" * 50)
    print("Loading data...")
    data = load_data()
    print("\n" + "=" * 50)
    print("Ready! Ask your SEO questions below.")
    print("Commands: 'save' = save last report | 'quit' = exit")
    print("=" * 50)

    last_question = ""
    last_answer = ""

    while True:
        print()
        question = input("Your question: ").strip()

        if question.lower() == 'quit':
            print("Goodbye!")
            break
        if question.lower() == 'save':
            if last_answer:
                save_report(last_question, last_answer)
            else:
                print("No analysis to save yet!")
            continue
        if not question:
            continue

        last_question = question
        last_answer = ask_ai(question, data)
        print("\nAI ANALYSIS:")
        print("=" * 50)
        print(last_answer)
        print("=" * 50)
        print("Type 'save' to save this report or ask another question.")

if __name__ == "__main__":
    main()
