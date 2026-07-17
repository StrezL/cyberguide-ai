# CyberGuide AI

CyberGuide AI is an intelligent security awareness platform that provides streamed, AI-generated explanations, defensive measures, and quizzes across eight cybersecurity domains.

## Features

- Internet Threats, Information Security, Cloud Security, Network Security, Social Engineering, Malware, Defensive Measures, and Cryptography
- Beginner, intermediate, and advanced learning levels
- Explanation, defensive-measures, and quiz modes
- Real-time streamed responses from the Groq LLM API
- Responsive lilac-themed interface for desktop and mobile
- Defensive-use system prompt and safe redirection
- Server-side API key protection
- Docker container and AWS App Runner-ready health endpoint

## Technology stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI, Pydantic, HTTPX
- AI: Groq API with `llama-3.3-70b-versatile` by default
- Deployment: Docker container on AWS App Runner

## Run locally

1. Create and activate a Python 3.12 virtual environment.
2. Install the packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your Groq API key.
4. Load the environment variables, then start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open `http://127.0.0.1:8000`.

Never commit `.env` or place the API key in frontend files.

## Run with Docker

```bash
docker build -t cyberguide-ai .
docker run --rm -p 8080:8080 -e GROQ_API_KEY="your-key" cyberguide-ai
```

Open `http://localhost:8080`. The health check is available at `/health`.

## AWS deployment outline

1. Create an Amazon ECR repository.
2. Authenticate Docker to ECR, build the image, tag it, and push it.
3. Create an AWS App Runner service using the ECR image.
4. Set port `8080` and health-check path `/health`.
5. Add `GROQ_API_KEY` as a secure App Runner environment variable.
6. Deploy and test the public HTTPS URL on desktop and mobile.
7. Add the final URL to the Concept Note and Project Report.

Configure an AWS Budget alert before deployment and pause or delete unused services after evaluation.

## Safety scope

The application is designed for education, awareness, prevention, and defensive security. Its system prompt refuses requests that would meaningfully enable unauthorized access, malware, credential theft, evasion, exploitation, or destructive activity.
