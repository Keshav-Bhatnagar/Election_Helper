# ElectionEdu

## Chosen Vertical: Election Process Education
ElectionEdu is a nonpartisan educational platform designed to empower citizens with knowledge about the democratic process. It provides an intuitive, accessible interface for voters to understand election mechanics, find personalized voting information, and get objective answers to complex electoral questions.

## Approach and Logic
The platform is built with a client-server architecture consisting of a premium glassmorphic frontend and a lightweight Python Flask backend. This design ensures that sensitive API keys are kept secure while delivering a state-of-the-art user experience. 

- **AI Chat Integration**: Powered by the Anthropic API (Claude), the AI assistant acts as a nonpartisan election expert. It receives a strict system prompt to remain objective and concise, answering questions regarding voter rights, registration deadlines, and election security.
- **Google Civic API Integration**: The backend queries two distinct Google Civic endpoints (`v2/voterinfo` and `v2/representatives`). By aggregating this data, the app dynamically provides users with their upcoming election dates, registered polling locations, and a list of their current elected representatives based on their residential address.

## How the Solution Works
1. **Interactive Timeline**: Users first engage with a 7-step visual journey detailing the electoral process—from Voter Registration to final Certification. Scroll animations and interactive nodes guide the learning experience.
2. **Personalized Lookup**: The user inputs their address into the Voter Information tool. The frontend makes a `fetch` request to the local `/api/civic` endpoint.
3. **Backend Proxying**: The Flask backend securely attaches the `GOOGLE_CIVIC_API_KEY` and forwards the request. It merges the data from the Google APIs and returns a clean JSON response.
4. **Data Visualization**: The frontend parses the response and dynamically generates premium UI cards displaying the user's specific election dates, polling hours, and local representatives.
5. **AI Q&A**: If the user has specific questions, they type them into the Chat Assistant. The backend proxies the request to Anthropic, returning real-time, objective guidance.

## Assumptions Made
- The user is inquiring about the United States electoral system, as the Google Civic Information API strictly supports U.S. addresses and elections.
- The user has an active internet connection to load external premium fonts (Google Fonts) and access the third-party APIs.
- The deployment environment supports Python 3.x and pip for dependency management.

## How to Run Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Keshav-Bhatnagar/Election_Helper.git
   cd Election_Helper
   ```

2. **Set up Environment Variables**:
   Create a `.env` file in the root directory based on `.env.example`:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_CIVIC_API_KEY=your_google_civic_key_here
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask Server**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8080`.
