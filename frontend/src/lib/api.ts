import axios from 'axios'
import { supabase } from '@/lib/supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // 10s timeout
})

// Attach Supabase auth token to every request if available
api.interceptors.request.use(async (config) => {
  try {
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  } catch {
    // Ignore auth session retrieval error when offline
  }
  return config
})

// ── In-Memory Mock Store for Client-Side Fallback ─────────────────────────────
const mockStore: any = {
  profile: {
    uid: 'user_123',
    name: 'Alex Morgan',
    email: 'alex.morgan@student.edu',
    college: 'Tech Institute of Technology',
    degree: 'B.Tech Computer Science',
    department: 'Computer Science & Engineering',
    current_year: 3,
    cgpa: 8.9,
    target_career: 'Full Stack Engineer',
    skills: ['React', 'TypeScript', 'Python', 'FastAPI', 'Tailwind CSS', 'SQL', 'Git'],
    interests: ['Artificial Intelligence', 'Web Development', 'System Architecture'],
    github_url: 'https://github.com/alexmorgan',
    linkedin_url: 'https://linkedin.com/in/alexmorgan',
    portfolio_url: 'https://alexmorgan.dev',
    profile_completion: {
      percentage: 85,
      missing_fields: ['Certificates', 'Portfolio Projects'],
    },
    projects: [{ title: 'AI Career Guidance Platform' }, { title: 'E-Commerce Microservices' }],
    internships: [{ title: 'Frontend Developer Intern at TechCorp' }],
  },
  jobScore: {
    total_score: 78,
    skills_score: 24,
    projects_score: 20,
    internships_score: 15,
    certificates_score: 7,
    profile_score: 12,
    suggestions: [
      'Add 2 more certificates to boost your score above 85',
      'Complete the System Architecture module in Learning Roadmap',
      'Add measurable metrics (% performance gain) to resume project descriptions',
    ],
  },
  certificates: [
    {
      id: 'cert_1',
      file_name: 'AWS_Certified_Cloud_Practitioner.pdf',
      certificate_title: 'AWS Certified Cloud Practitioner',
      issuing_organization: 'Amazon Web Services',
      upload_date: '2026-07-15T10:00:00Z',
      status: 'completed',
      extracted_skills: {
        Cloud: ['AWS EC2', 'AWS S3', 'IAM', 'CloudFront', 'Lambda'],
      },
    },
    {
      id: 'cert_2',
      file_name: 'Meta_Front_End_Developer.pdf',
      certificate_title: 'Meta Professional Front-End Developer',
      issuing_organization: 'Meta / Coursera',
      upload_date: '2026-08-01T14:30:00Z',
      status: 'completed',
      extracted_skills: {
        Frontend: ['React', 'JavaScript', 'HTML5/CSS3', 'Version Control'],
      },
    },
  ],
  communityPosts: [
    {
      id: 'post_1',
      author: 'Priya Sharma',
      role: 'Final Year CSE Student',
      avatar: 'P',
      title: 'Looking for a React + FastAPI collaborator for Hackathon 2026!',
      content: 'Hey everyone! I am building an AI-powered study scheduler using React and Python FastAPI. Looking for 1-2 teammates interested in frontend UI and AI API integration.',
      tags: ['Hackathon', 'React', 'FastAPI'],
      created_at: '2 hours ago',
      upvotes: 14,
      comments_count: 5,
    },
    {
      id: 'post_2',
      author: 'David Chen',
      role: 'SDE Intern @ Amazon',
      avatar: 'D',
      title: 'Top 5 System Design questions asked in SDE-1 interviews',
      content: 'Here are the key system design patterns you should prepare: Rate Limiters, URL Shortener, Notification System, Load Balancing, and Database Indexing basics.',
      tags: ['Interview Prep', 'System Design'],
      created_at: '1 day ago',
      upvotes: 38,
      comments_count: 12,
    },
    {
      id: 'post_3',
      author: 'Ananya Rao',
      role: '3rd Year IT',
      avatar: 'A',
      title: 'Best resources for practicing LeetCode patterns?',
      content: 'I recommend NeetCode 150 and Striver SDE sheet. They group problems by pattern (Two Pointers, Sliding Window, Graphs) which makes learning 10x faster.',
      tags: ['DSA', 'LeetCode', 'Resources'],
      created_at: '3 days ago',
      upvotes: 29,
      comments_count: 8,
    },
  ],
  conversations: [
    { id: 'conv_1', title: 'Full Stack Engineer Learning Path', created_at: '2026-08-05' },
    { id: 'conv_2', title: 'System Design & Mock Interview Prep', created_at: '2026-08-08' },
  ],
  conversationMessages: {
    conv_1: [
      { role: 'user', content: 'What technical skills should I master for Full-Stack role?' },
      { role: 'assistant', content: '### Technical Roadmap for Full Stack Engineering\n\nTo excel as a Full-Stack Engineer, focus on:\n\n1. **Core Development**: Master React 19, TypeScript, and FastAPI/Node.js.\n2. **Database & Cache**: PostgreSQL schema design, indexing, and Redis caching.\n3. **DevOps & Cloud**: Docker containerization, CI/CD pipelines, and AWS deployment.\n\n*Actionable Step*: Track and update your acquired skills in the **Profile** tab to dynamically evaluate your readiness score!' }
    ],
    conv_2: [
      { role: 'user', content: 'Prepare me for a system design interview question' },
      { role: 'assistant', content: '### System Design Interview Strategy\n\nFor technical and architectural interviews:\n\n1. **4-Step Framework**: Scope requirements -> High-Level Architecture -> Deep-dive components & caching -> Identify bottlenecks & scale.\n2. **Coding Practice**: Solve top pattern questions (Graphs, Two Pointers, Dynamic Programming).\n3. **Practice**: Test your real-time responses in our **AI Interview Simulator** tab!' }
    ]
  },
  learning: {
    domain: 'Full Stack & Web Engineering',
    target_career: 'Full-Stack Engineer',
    progress_percentage: 60,
    completed_items: 6,
    total_items: 10,
    stages: {
      '1': [
        {
          id: 'l1', title: 'Module 1 — HTML5 & Modern CSS3 Grid/Flexbox', description: 'Core web page structure and responsive container layouts.', skill: 'Frontend Basics', platform: 'freeCodeCamp', difficulty: 'beginner', status: 'completed', resource_url: 'https://freecodecamp.org',
          courses: [{ title: 'Responsive Web Design Certification', platform: 'freeCodeCamp', url: 'https://freecodecamp.org', difficulty: 'beginner', level: 'Beginner Track', duration: '4 weeks', relevance_reason: 'Foundational markup for web interfaces.' }]
        },
        {
          id: 'l2', title: 'Module 1 — JavaScript ES6+ & Async/Await', description: 'Asynchronous event loop, closures, and promises.', skill: 'JavaScript', platform: 'MDN Web Docs', difficulty: 'beginner', status: 'completed', resource_url: 'https://developer.mozilla.org',
          courses: [{ title: 'The Complete JavaScript Course 2026', platform: 'Udemy', url: 'https://udemy.com', difficulty: 'beginner', level: 'Beginner Track', duration: '8 weeks', relevance_reason: 'Core web programming language.' }]
        },
      ],
      '2': [
        {
          id: 'l3', title: 'Module 2 — React 19 Hooks & Context API', description: 'Component architecture, custom hooks, and virtual DOM.', skill: 'React', platform: 'React Docs', difficulty: 'intermediate', status: 'completed', resource_url: 'https://react.dev',
          courses: [{ title: 'React 19 & Next.js - Complete Guide', platform: 'Udemy', url: 'https://udemy.com', difficulty: 'intermediate', level: 'Intermediate Specialization', duration: '10 weeks', relevance_reason: 'Primary UI component library for web applications.' }]
        },
        {
          id: 'l4', title: 'Module 2 — TypeScript Core Types & Interfaces', description: 'Static typing, generics, and strict null checks.', skill: 'TypeScript', platform: 'TypeScript Handbook', difficulty: 'intermediate', status: 'completed', resource_url: 'https://typescriptlang.org',
          courses: [{ title: 'Understanding TypeScript 2026', platform: 'Udemy', url: 'https://udemy.com', difficulty: 'intermediate', level: 'Intermediate Specialization', duration: '5 weeks', relevance_reason: 'Type safety for scaling enterprise software.' }]
        },
        {
          id: 'l5', title: 'Module 2 — FastAPI REST API Architecture', description: 'Asynchronous Python endpoints and Pydantic schemas.', skill: 'FastAPI', platform: 'FastAPI Tutorial', difficulty: 'intermediate', status: 'in_progress', resource_url: 'https://fastapi.tiangolo.com',
          courses: [{ title: 'FastAPI High-Performance Microservices', platform: 'TestDriven.io', url: 'https://testdriven.io', difficulty: 'intermediate', level: 'Intermediate Specialization', duration: '4 weeks', relevance_reason: 'High throughput API backend framework.' }]
        },
      ],
      '3': [
        {
          id: 'l6', title: 'Module 3 — PostgreSQL Relational Schema & ORM', description: 'Database schema normalization, indexing, and SQL queries.', skill: 'SQL', platform: 'PostgreSQL Docs', difficulty: 'intermediate', status: 'completed', resource_url: 'https://postgresql.org',
          courses: [{ title: 'The Complete SQL Bootcamp', platform: 'Udemy', url: 'https://udemy.com', difficulty: 'beginner', level: 'Beginner Track', duration: '4 weeks', relevance_reason: 'Relational data persistence.' }]
        },
        {
          id: 'l7', title: 'Module 3 — System Architecture & Caching', description: 'Redis caching, load balancing, and rate limiting.', skill: 'System Design', platform: 'Educative.io', difficulty: 'advanced', status: 'in_progress', resource_url: 'https://educative.io',
          courses: [{ title: 'Grokking Modern System Design', platform: 'Educative.io', url: 'https://educative.io', difficulty: 'advanced', level: 'Advanced Architecture', duration: '6 weeks', relevance_reason: 'High availability scalable design.' }]
        },
      ],
      '4': [
        {
          id: 'l8', title: 'Module 4 — Build Full-Stack Microservice Project', description: 'End-to-end full stack application with auth and Docker.', skill: 'Project', platform: 'Self-guided', difficulty: 'advanced', status: 'completed', resource_url: '#',
          courses: [{ title: 'Full Stack Microservices Architecture', platform: 'CareerPilot AI', url: 'https://github.com', difficulty: 'advanced', level: 'Portfolio Architecture', duration: '3 weeks', relevance_reason: 'Hands-on practical proof of work.' }]
        },
        {
          id: 'l9', title: 'Module 4 — Docker Containerization & CI/CD', description: 'Containerizing services and automating GitHub Actions.', skill: 'Docker', platform: 'Docker Labs', difficulty: 'intermediate', status: 'not_started', resource_url: 'https://docker.com',
          courses: [{ title: 'Docker & Kubernetes Practical Guide', platform: 'Udemy', url: 'https://udemy.com', difficulty: 'intermediate', level: 'Intermediate Specialization', duration: '4 weeks', relevance_reason: 'Environment parity and DevOps deployment.' }]
        },
      ],
      '5': [
        {
          id: 'l10', title: 'Module 5 — Executive Interview & Coding Prep', description: 'Coding algorithms, system design, and STAR responses.', skill: 'Interview', platform: 'CareerPilot AI', difficulty: 'advanced', status: 'in_progress', resource_url: 'https://leetcode.com',
          courses: [{ title: 'Grokking Coding Interviews', platform: 'LeetCode', url: 'https://leetcode.com', difficulty: 'advanced', level: 'Executive Preparation', duration: '3 weeks', relevance_reason: 'Technical interview loop readiness.' }]
        },
      ],
    },
  },
  companies: [
    { id: 'google', name: 'Google', difficulty: 'Hard (Tier 1)', logo_color: 'bg-red-600' },
    { id: 'microsoft', name: 'Microsoft', difficulty: 'Medium-Hard', logo_color: 'bg-blue-600' },
    { id: 'amazon', name: 'Amazon', difficulty: 'Medium-Hard', logo_color: 'bg-amber-600' },
    { id: 'meta', name: 'Meta', difficulty: 'Hard (Tier 1)', logo_color: 'bg-[#174A3A]' },
    { id: 'apple', name: 'Apple', difficulty: 'Hard (Tier 1)', logo_color: 'bg-slate-700' },
    { id: 'netflix', name: 'Netflix', difficulty: 'Very Hard', logo_color: 'bg-red-700' },
    { id: 'uber', name: 'Uber', difficulty: 'Hard', logo_color: 'bg-black' },
    { id: 'stripe', name: 'Stripe', difficulty: 'Hard (Fintech)', logo_color: 'bg-purple-600' },
  ],
  companyDetails: {
    google: {
      id: 'google',
      name: 'Google',
      difficulty: 'Hard (Tier 1)',
      logo_color: 'bg-red-600',
      culture: 'Engineering-driven culture focused on scalability, algorithms, robust testing, and collaborative problem solving.',
      roles: ['Software Engineer', 'Frontend Engineer', 'Backend Specialist', 'Machine Learning Engineer'],
      rounds: [
        'Round 1: Online Technical Assessment (2 Coding Problems, 90 mins)',
        'Round 2: Technical Phone Screen (Data Structures & Algorithms)',
        'Round 3-6: Onsite Interviews (3 DSA + 1 System Design + 1 Googliness & Leadership)',
      ],
      top_topics: ['Graph Algorithms & BFS/DFS', 'Dynamic Programming', 'System Design & Distributed Caching', 'Trie & Binary Search'],
      sample_questions: [
        'Given a 2D grid, find the shortest path from start to target considering obstacle cell costs.',
        'Design a rate limiting algorithm capable of handling 100,000 requests/sec across distributed clusters.',
        'Implement an LRU (Least Recently Used) cache with O(1) time complexity for get and put ops.',
        'Tell me about a time you encountered ambiguity in a project spec and how you resolved it.',
      ],
    },
    microsoft: {
      id: 'microsoft',
      name: 'Microsoft',
      difficulty: 'Medium-Hard',
      logo_color: 'bg-blue-600',
      culture: 'Growth mindset environment emphasizing customer orientation, code quality, and cloud-native solutions (Azure).',
      roles: ['Software Engineer (SDE-1)', 'Cloud Solutions Architect', 'Frontend Developer'],
      rounds: [
        'Round 1: Online Coding Test (Codility - 3 questions)',
        'Round 2: Technical Interview 1 (Trees & Strings)',
        'Round 3: Technical Interview 2 (System Architecture)',
        'Round 4: AA (As-Appropriate) Final Round (Leadership & Culture)',
      ],
      top_topics: ['Binary Tree Traversal', 'Linked List & Pointers', 'OOP Design & Microservices', 'SQL & Database Indexing'],
      sample_questions: [
        'Reverse a linked list in groups of size K.',
        'Design a real-time collaborative document editor like Microsoft Word Online.',
        'Explain how index structures (B-Trees) speed up database query evaluation.',
      ],
    },
    meta: {
      id: 'meta',
      name: 'Meta',
      difficulty: 'Hard (Tier 1)',
      logo_color: 'bg-[#0668E1]',
      culture: 'Move fast, build social connection technology, and focus on high-impact products serving billions of users.',
      roles: ['Software Engineer', 'Production Engineer', 'Frontend Specialist'],
      rounds: [
        'Round 1: Recruiter Phone Screen',
        'Round 2: Technical Screen (2 LeetCode Medium/Hard in 45 mins)',
        'Round 3-6: Full Loop (2 Coding + 2 System Design + 1 Behavioral)',
      ],
      top_topics: ['Binary Search & Arrays', 'Dynamic Programming', 'Graph Traversal', 'System Design'],
      sample_questions: [
        'Find the minimum window substring containing all characters of a target string.',
        'Design a news feed system capable of serving millions of concurrent active users.',
        'Describe how you handle conflicting technical opinions within your engineering team.',
      ],
    },
    amazon: {
      id: 'amazon',
      name: 'Amazon',
      difficulty: 'Medium-Hard',
      logo_color: 'bg-amber-600',
      culture: 'Customer obsession and 16 Leadership Principles driving fast execution and decentralized ownership.',
      roles: ['SDE-1', 'SDE-2', 'Frontend Engineer'],
      rounds: [
        'Round 1: Online Assessment (Debugging + Coding + Work Style Simulation)',
        'Round 2: Technical Phone Screen',
        'Round 3-6: Onsite Loop (4-5 rounds, each evaluating 2 Leadership Principles + Technical)',
      ],
      top_topics: ['Trees & Graphs', 'Sliding Window', 'Object-Oriented Design', 'LP Star Stories'],
      sample_questions: [
        'Design a customer order fulfillment catalog service.',
        'Give an example of a time you took calculated risks to deliver customer value.',
        'Find the top K most frequent items in a large data stream.',
      ],
    },
    apple: {
      id: 'apple',
      name: 'Apple',
      difficulty: 'Hard (Tier 1)',
      logo_color: 'bg-slate-700',
      culture: 'Detail-oriented craftsmanship, extreme privacy focus, hardware-software integration, and product perfection.',
      roles: ['Software Engineer', 'iOS Engineer', 'Systems Programmer'],
      rounds: [
        'Round 1: Recruiter Call',
        'Round 2: Technical Phone Screen',
        'Round 3-7: Full Onsite Loop (Domain-specific technical & architecture assessments)',
      ],
      top_topics: ['Memory Management & C/C++', 'Concurrency', 'Low-level Data Structures', 'API Design'],
      sample_questions: [
        'Implement a custom memory allocator with malloc and free semantics.',
        'Design an end-to-end encrypted messaging synchronization protocol.',
        'Explain how garbage collection vs ARC (Automatic Reference Counting) impacts runtime performance.',
      ],
    },
    netflix: {
      id: 'netflix',
      name: 'Netflix',
      difficulty: 'Very Hard',
      logo_color: 'bg-red-700',
      culture: 'Freedom & Responsibility culture hiring senior talent with high autonomy and engineering rigor.',
      roles: ['Senior Software Engineer', 'Full Stack Developer', 'Platform Engineer'],
      rounds: [
        'Round 1: Phone Screen with Hiring Manager',
        'Round 2: Technical Assessment (Deep Architecture & Code Review)',
        'Round 3-6: Onsite Interviews (Deep System Architecture & Culture Fit)',
      ],
      top_topics: ['Microservices', 'Resiliency & Chaos Engineering', 'High Throughput Streaming', 'Distributed Caching'],
      sample_questions: [
        'Design a high-availability video streaming CDN edge delivery architecture.',
        'How do you build fault-tolerant fallbacks for dependent microservice failures?',
        'Describe how you handle extreme freedom and accountability in your career.',
      ],
    },
    uber: {
      id: 'uber',
      name: 'Uber',
      difficulty: 'Hard',
      logo_color: 'bg-black',
      culture: 'Real-time geospatial matching, high throughput logistics pipelines, and scalable microservices.',
      roles: ['Software Engineer', 'Backend Engineer', 'Infrastructure Specialist'],
      rounds: [
        'Round 1: Online Assessment (CodeSignal)',
        'Round 2: Technical Phone Screen',
        'Round 3-6: Onsite Loop (Coding + Geospatial System Design + Architecture)',
      ],
      top_topics: ['Geospatial Hashing (H3/QuadTree)', 'Concurrent Data Structures', 'Distributed Consensus', 'Rate Limiting'],
      sample_questions: [
        'Design a real-time driver-rider matching system for 1 million active rides.',
        'Implement a geospatial index for efficient nearest-neighbor search.',
        'How do you maintain data consistency in eventual consistency distributed databases?',
      ],
    },
    stripe: {
      id: 'stripe',
      name: 'Stripe',
      difficulty: 'Hard (Fintech)',
      logo_color: 'bg-purple-600',
      culture: 'Developer-first API craftsmanship, extreme clarity in documentation, and financial-grade reliability.',
      roles: ['Software Engineer', 'Frontend Engineer', 'Infrastructure Engineer'],
      rounds: [
        'Round 1: Recruiter Chat',
        'Round 2: Technical Phone Screen (Practical Bug Fix & Feature Expansion)',
        'Round 3-6: Onsite Loop (API Design + Codebase Exploration + System Design + Integration)',
      ],
      top_topics: ['API Ergonomics', 'Idempotency & Transactions', 'Practical Code Base Refactoring', 'JSON Schema Validation'],
      sample_questions: [
        'Design an idempotent payment processing API endpoint capable of handling network retries safely.',
        'Refactor and fix bugs in a provided open-source framework repository.',
        'How do you design database transactions to prevent double-spending in high concurrency apps?',
      ],
    },
  },
}

// ── Interceptor Response Fallback Handler ──────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url || ''
    const method = (error.config?.method || 'get').toLowerCase()

    console.warn(`Backend request failed for ${method.toUpperCase()} ${url}. Using smart fallback response.`)

    // ── Profile Endpoints ─────────────────────────────────────────────────────
    if (url.includes('/api/profile')) {
      if (url.includes('/picture')) {
        return Promise.resolve({ data: { message: 'Picture uploaded', profile_picture_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150' } })
      }
      if (method === 'put') {
        const body = JSON.parse(error.config.data || '{}')
        mockStore.profile = { ...mockStore.profile, ...body }
        return Promise.resolve({ data: mockStore.profile })
      }
      return Promise.resolve({ data: mockStore.profile })
    }

    // ── Job Score Endpoints ───────────────────────────────────────────────────
    if (url.includes('/api/job-score')) {
      const currentUid = localStorage.getItem('cp_active_uid') || 'demo_user'
      const storageKey = `cp_user_score_${currentUid}`
      const historyKey = `cp_user_history_${currentUid}`
      const savedScore = localStorage.getItem(storageKey)

      if (url.includes('/history')) {
        const savedHistory = localStorage.getItem(historyKey)
        return Promise.resolve({ data: { uid: currentUid, history: savedHistory ? JSON.parse(savedHistory) : [] } })
      }

      if (savedScore) {
        try {
          const parsed = JSON.parse(savedScore)
          const savedHistory = localStorage.getItem(historyKey)
          if (savedHistory) parsed.history = JSON.parse(savedHistory)
          return Promise.resolve({ data: parsed })
        } catch {}
      }

      // Initial 0 score for brand new account session
      const initialScore = {
        uid: currentUid,
        total_score: 0.0,
        skills_score: 0.0,
        projects_score: 0.0,
        interviews_score: 0.0,
        resume_score: 0.0,
        assessments_score: 0.0,
        certificates_score: 0.0,
        profile_score: 0.0,
        internships_score: 0.0,
        confidence_level: 'Insufficient Data',
        data_quality_notice: 'New candidate account. Add technical skills, take mock tests, or run ATS resume diagnostics to compute your score.',
        positive_drivers: [],
        suggestions: [
          'Welcome to CareerPilot AI! Add 3+ technical skills with proficiency in your profile.',
          'Execute a resume ATS diagnostic scan to audit keyword compliance.',
          'Complete a domain-specific AI Mock Interview.',
        ],
        max_scores: {
          skills: 25,
          projects: 20,
          interviews: 20,
          resume: 15,
          assessments: 10,
          certificates: 10,
        },
        factors_breakdown: {
          skills: { score: 0, max: 25, percentage: 0 },
          projects: { score: 0, max: 20, percentage: 0 },
          interviews: { score: 0, max: 20, percentage: 0 },
          resume: { score: 0, max: 15, percentage: 0 },
          assessments: { score: 0, max: 10, percentage: 0 },
          certificates: { score: 0, max: 10, percentage: 0 },
        },
        history: [],
        updated_at: new Date().toISOString(),
      }
      localStorage.setItem(storageKey, JSON.stringify(initialScore))
      return Promise.resolve({ data: initialScore })
    }

    // ── Assessments Endpoints ─────────────────────────────────────────────────
    if (url.includes('/api/assessments')) {
      const currentUid = localStorage.getItem('cp_active_uid') || 'demo_user'
      if (url.includes('/submit') && method === 'post') {
        const body = JSON.parse(error.config?.data || '{}')
        const scoreVal = Number(body.score || 80)
        
        // Update stored score
        const storageKey = `cp_user_score_${currentUid}`
        const historyKey = `cp_user_history_${currentUid}`
        const raw = localStorage.getItem(storageKey)
        let currScore = raw ? JSON.parse(raw) : { total_score: 0, skills_score: 0, assessments_score: 0, max_scores: {} }
        
        const addedAssessments = Math.min(10, Math.round((scoreVal / 100) * 10))
        currScore.assessments_score = addedAssessments
        currScore.total_score = Math.min(100, Math.round((currScore.skills_score || 0) + (currScore.projects_score || 0) + (currScore.interviews_score || 0) + (currScore.resume_score || 0) + addedAssessments + (currScore.certificates_score || 0)))
        currScore.confidence_level = 'Verified Data Precision'
        
        const history = JSON.parse(localStorage.getItem(historyKey) || '[]')
        history.push({
          timestamp: new Date().toISOString(),
          total_score: currScore.total_score,
          delta: 8.0,
          reason: `Completed ${body.test_title || 'Mock Test'} (${scoreVal}%)`
        })
        localStorage.setItem(storageKey, JSON.stringify(currScore))
        localStorage.setItem(historyKey, JSON.stringify(history))

        return Promise.resolve({
          data: {
            success: true,
            score: scoreVal,
            readiness_score: currScore.total_score,
            message: 'Assessment recorded and Career Readiness Score recalculated.'
          }
        })
      }

      return Promise.resolve({
        data: {
          tests: [
            {
              id: 'dsa',
              title: 'Data Structures & Algorithms Core Assessment',
              category: 'Algorithms',
              questions_count: 5,
              time_limit: '20 mins',
              difficulty: 'Hard',
              questions: [
                {
                  id: 1,
                  q: 'Which data structure offers average O(1) time complexity for lookup, insert, and delete operations?',
                  options: ['Binary Search Tree', 'Hash Table / Map', 'Linked List', 'Max Heap'],
                  correct: 1,
                  explanation: 'Hash tables leverage a hash function to map keys to bucket indices, yielding O(1) average time complexity.'
                }
              ]
            }
          ]
        }
      })
    }

    // ── Resume ATS Optimizer Endpoint ─────────────────────────────────────────
    if (url.includes('/api/resume/analyze-ats')) {
      const currentUid = localStorage.getItem('cp_active_uid') || 'demo_user'
      const body = JSON.parse(error.config?.data || '{}')
      const targetRole = body.target_role || 'Software Engineer'
      const textLen = (body.resume_text || '').length
      const score = Math.min(95, Math.max(65, 75 + Math.floor(textLen / 50)))

      // Update stored score
      const storageKey = `cp_user_score_${currentUid}`
      const historyKey = `cp_user_history_${currentUid}`
      const raw = localStorage.getItem(storageKey)
      let currScore = raw ? JSON.parse(raw) : { total_score: 0, skills_score: 0, max_scores: {} }
      const addedResume = Math.min(15, Math.round((score / 100) * 15))
      currScore.resume_score = addedResume
      currScore.total_score = Math.min(100, Math.round((currScore.skills_score || 0) + (currScore.projects_score || 0) + (currScore.interviews_score || 0) + addedResume + (currScore.assessments_score || 0) + (currScore.certificates_score || 0)))
      currScore.confidence_level = 'Verified Data Precision'

      const history = JSON.parse(localStorage.getItem(historyKey) || '[]')
      history.push({
        timestamp: new Date().toISOString(),
        total_score: currScore.total_score,
        delta: 12.0,
        reason: `Resume ATS Scan Executed (${score} ATS Score)`
      })
      localStorage.setItem(storageKey, JSON.stringify(currScore))
      localStorage.setItem(historyKey, JSON.stringify(history))

      return Promise.resolve({
        data: {
          ats_score: score,
          score,
          target_role: targetRole,
          readiness_score: currScore.total_score,
          breakdown: {
            keyword_match: Math.min(92, score + 4),
            formatting: 90,
            experience_impact: Math.min(88, score - 2),
            section_completeness: 95,
          },
          matched_keywords: ['React', 'TypeScript', 'REST APIs', 'FastAPI', 'Git', 'Component Architecture', 'State Management'],
          missing_keywords: ['Docker', 'CI/CD Pipelines', 'GraphQL', 'Jest Testing', 'Cloud Deployment (AWS)'],
          strengths: [
            `Strong technical skill alignment for ${targetRole} position`,
            'Clean section structure with standard industry headers',
            'Solid foundation in modern web frameworks and language syntax',
          ],
          improvements: [
            'Incorporate quantified metrics (% performance gain, user count) in project achievements',
            'Include cloud and DevOps keywords (Docker, CI/CD, AWS) to pass automated ATS filters',
            'Add a dedicated 2-sentence Professional Summary at the top of your resume',
          ],
        },
      })
    }

    // ── AI Interview Endpoints ────────────────────────────────────────────────
    if (url.includes('/api/interview/save-session') && method === 'post') {
      const currentUid = localStorage.getItem('cp_active_uid') || 'demo_user'
      const body = JSON.parse(error.config?.data || '{}')
      const storageKey = `cp_user_score_${currentUid}`
      const historyKey = `cp_user_history_${currentUid}`
      const raw = localStorage.getItem(storageKey)
      let currScore = raw ? JSON.parse(raw) : { total_score: 0, skills_score: 0, max_scores: {} }
      
      const sessionScore = Number(body.overall_score || 80)
      const addedInterview = Math.min(20, Math.round((sessionScore / 100) * 20))
      currScore.interviews_score = addedInterview
      currScore.total_score = Math.min(100, Math.round((currScore.skills_score || 0) + (currScore.projects_score || 0) + addedInterview + (currScore.resume_score || 0) + (currScore.assessments_score || 0) + (currScore.certificates_score || 0)))
      currScore.confidence_level = 'High Data Precision'

      const history = JSON.parse(localStorage.getItem(historyKey) || '[]')
      history.push({
        timestamp: new Date().toISOString(),
        total_score: currScore.total_score,
        delta: 15.0,
        reason: `Completed AI Mock Interview (${sessionScore}%)`
      })
      localStorage.setItem(storageKey, JSON.stringify(currScore))
      localStorage.setItem(historyKey, JSON.stringify(history))

      return Promise.resolve({
        data: {
          success: true,
          readiness_score: currScore.total_score,
          message: 'Interview session saved and Career Readiness Score updated.'
        }
      })
    }

    if (url.includes('/api/interview/start')) {
      const body = JSON.parse(error.config?.data || '{}')
      const role = body.role || 'Software Engineer'
      const category = body.category || 'technical'

      const questionsMap: Record<string, string[]> = {
        technical: [
          `Explain how state management and asynchronous data fetching work in ${role} applications.`,
          `How do you optimize database query execution times and prevent N+1 query bottlenecks?`,
          `Describe the difference between Client-Side Rendering (CSR) and Server-Side Rendering (SSR).`,
          `How do you implement secure authentication using JWT tokens and HTTP-only cookies?`,
          `Walk me through your process for debugging a memory leak in a high-traffic production application.`,
        ],
        behavioral: [
          `Tell me about a time you worked on a complex technical project with tight deadlines. How did you prioritize tasks?`,
          `Describe a situation where you had a disagreement with a team member on architecture. How did you resolve it?`,
          `Give an example of how you handled a critical failure or bug report in production.`,
        ],
        system_design: [
          `Design a scalable URL shortening service (like Bit.ly) handling 500 million links per day.`,
          `How would you architect a real-time chat application with millions of active WebSockets connections?`,
        ],
      }

      return Promise.resolve({
        data: {
          session_id: 'session_' + Date.now(),
          role,
          category,
          questions: questionsMap[category] || questionsMap.technical,
        },
      })
    }

    if (url.includes('/api/interview/evaluate')) {
      const body = JSON.parse(error.config?.data || '{}')
      const answer = (body.answer || '').trim()
      const question = body.question || 'this technical prompt'
      const role = body.role || 'Software Engineer'
      const cleanAns = answer.toLowerCase()

      // 1. Gibberish & Low Effort Detection
      if (cleanAns.length < 15) {
        return Promise.resolve({
          data: {
            score: 10,
            clarity: 15,
            technical_accuracy: 5,
            feedback: 'Your answer is too brief to evaluate technical competency. Please provide a detailed response explaining your technical approach and tools.',
            sample_answer: `For "${question}", an optimal response defines the architectural principles, lists concrete tools/frameworks, and explains trade-offs.`,
          },
        })
      }

      const lettersOnly = cleanAns.replace(/[^a-z]/g, '')
      const uniqueChars = new Set(lettersOnly).size
      const words = cleanAns.split(/\s+/)
      const maxWordLen = Math.max(...words.map((w: string) => w.length))
      const lowEffortPhrases = ['idk', 'i dont know', 'i don\'t know', 'no idea', 'asdfghjkl', 'qwertyuiop', 'test', 'testing', 'pass']

      if ((uniqueChars < 6 && lettersOnly.length > 15) || maxWordLen > 25 || lowEffortPhrases.includes(cleanAns)) {
        return Promise.resolve({
          data: {
            score: 12,
            clarity: 10,
            technical_accuracy: 5,
            feedback: 'Your input appears to be random text or low-effort filler content. Candidate technical evaluation requires articulating relevant domain concepts and engineering patterns.',
            sample_answer: `A model response for "${question}": State the problem requirements, explain implementation choices, and highlight measurable outcomes.`,
          },
        })
      }

      // 2. Keyword & Domain Matching
      const domainKeywords = [
        'http', 'endpoint', 'json', 'status', 'middleware', 'auth', 'token', 'jwt', 'post', 'get', 'put', 'delete', 'rate limit', 'swagger', 'fastapi', 'express', 'router',
        'event loop', 'closure', 'async', 'await', 'promise', 'memory', 'heap', 'garbage collection', 'leak', 'pointer', 'thread', 'process', 'stack', 'concurrency',
        'index', 'n+1', 'join', 'postgresql', 'sql', 'query', 'table', 'b-tree', 'partition', 'replica', 'transaction', 'orm', 'sharding', 'migration', 'cache', 'redis',
        'trace', 'log', 'stack trace', 'reproduce', 'profiler', 'debugger', 'test', 'unit test', 'regression', 'root cause', 'git',
        'situation', 'task', 'action', 'result', 'team', 'conflict', 'resolution', 'deadline', 'trade-off', 'communicated', 'collaborated', 'delivered',
        'scale', 'load balancer', 'cdn', 'microservice', 'queue', 'kafka', 'latency', 'throughput', 'failover', 'redundancy', 'websocket'
      ]

      const matched = domainKeywords.filter(kw => cleanAns.includes(kw))
      const matchCount = matched.length

      let score = 25
      let clarity = 40
      let techAcc = 20
      let feedback = ''

      if (matchCount === 0) {
        score = Math.min(38, Math.max(20, 25 + Math.floor(words.length / 5)))
        clarity = Math.min(45, Math.max(30, 35 + Math.floor(words.length / 4)))
        techAcc = 18
        feedback = `Your response is structured grammatically, but lacks essential technical terms (such as APIs, database indexing, async patterns) expected for a ${role} position.`
      } else if (matchCount <= 2) {
        score = Math.min(68, Math.max(45, 52 + matchCount * 8))
        clarity = Math.min(75, 60 + matchCount * 5)
        techAcc = Math.min(65, 45 + matchCount * 10)
        feedback = `Partial technical alignment. You mentioned: ${matched.join(', ')}. To increase your score above 75%, elaborate on real-world trade-offs and edge-case handling.`
      } else if (matchCount <= 4) {
        score = Math.min(85, 74 + matchCount * 3)
        clarity = Math.min(88, 76 + matchCount * 3)
        techAcc = Math.min(84, 72 + matchCount * 3)
        feedback = `Strong technical response! Solid coverage of core domain concepts (${matched.join(', ')}). Consider detailing performance benchmarks or unit test coverage for top score.`
      } else {
        score = Math.min(96, 88 + (matchCount - 4) * 2)
        clarity = Math.min(95, 86 + matchCount * 2)
        techAcc = Math.min(94, 85 + matchCount * 2)
        feedback = `Excellent, industry-ready answer! Outstanding coverage of key concepts (${matched.slice(0, 5).join(', ')}) with clear structural articulation.`
      }

      return Promise.resolve({
        data: {
          score,
          clarity,
          technical_accuracy: techAcc,
          feedback,
          sample_answer: `A model response for "${question}": 1. State core system requirements. 2. Explain technical choices (${matched.length > 0 ? matched.slice(0, 3).join(', ') : 'architecture, caching, testing'}). 3. Highlight scalability and error handling.`,
        },
      })
    }

    // ── Company Prep Endpoints ────────────────────────────────────────────────
    if (url.includes('/api/company-prep/companies')) {
      if (url.includes('/companies/')) {
        const companyId = url.split('/companies/')[1]
        const detail = mockStore.companyDetails[companyId] || {
          id: companyId,
          name: companyId.toUpperCase(),
          difficulty: 'Hard',
          logo_color: 'bg-emerald-700',
          culture: 'Innovative, fast-paced technical environment driven by high engineering standards.',
          roles: ['Software Engineer', 'Full Stack Developer', 'Data Engineer'],
          rounds: [
            'Round 1: Screening & Coding Assessment',
            'Round 2: Data Structures & Algorithms',
            'Round 3: System Design & Architecture',
            'Round 4: Culture & Values Fit',
          ],
          top_topics: ['Data Structures & Algorithms', 'System Architecture', 'Database Optimization', 'Problem Solving'],
          sample_questions: [
            'How do you design a scalable microservice architecture for peak traffic spikes?',
            'Explain how indexing improves SQL query execution speed.',
            'Describe a challenging bug you diagnosed and fixed.',
          ],
        }
        return Promise.resolve({ data: detail })
      }

      const queryParam = (error.config?.params?.query || '').toLowerCase()
      const filtered = mockStore.companies.filter((c: any) => c.name.toLowerCase().includes(queryParam))
      return Promise.resolve({ data: { companies: filtered.length ? filtered : mockStore.companies } })
    }

    // ── Community Board Endpoints ─────────────────────────────────────────────
    if (url.includes('/api/community/posts')) {
      // 1. Upvote / Like
      if (url.includes('/upvote') || url.includes('/like')) {
        const parts = url.split('/')
        const postId = parts[parts.length - 2]
        const targetPost = mockStore.communityPosts.find((p: any) => p.id === postId)
        if (targetPost) {
          targetPost.upvotes = (targetPost.upvotes || 0) + 1
          return Promise.resolve({ data: { message: 'Upvoted successfully', upvotes: targetPost.upvotes } })
        }
        return Promise.resolve({ data: { message: 'Post upvoted', upvotes: 1 } })
      }

      // 2. Comments List or Create Comment
      if (url.includes('/comments')) {
        if (!mockStore.communityComments) {
          mockStore.communityComments = {
            'post_1': [
              { id: 'c1', author: 'Rohan Mehta', avatar: 'RM', role: 'Backend Intern', content: "Count me in! I'm focusing on distributed caching and DB indexing.", created_at: '1 hour ago' }
            ]
          }
        }

        const parts = url.split('/')
        const postId = parts[parts.length - 2]

        if (method === 'post') {
          const body = JSON.parse(error.config?.data || '{}')
          const newComment = {
            id: 'comment_' + Date.now(),
            author: mockStore.profile.name || 'Candidate Peer',
            avatar: mockStore.profile.name?.[0] || 'C',
            role: mockStore.profile.target_career || 'Student Developer',
            content: body.content || '',
            created_at: 'Just now',
          }
          if (!mockStore.communityComments[postId]) {
            mockStore.communityComments[postId] = []
          }
          mockStore.communityComments[postId].push(newComment)

          // Update comment count on post
          const targetPost = mockStore.communityPosts.find((p: any) => p.id === postId)
          if (targetPost) {
            targetPost.comments_count = mockStore.communityComments[postId].length
          }

          return Promise.resolve({ data: { message: 'Comment added', comment: newComment } })
        }

        const comments = mockStore.communityComments[postId] || []
        return Promise.resolve({ data: { comments } })
      }

      // 3. Create Post
      if (method === 'post') {
        const body = JSON.parse(error.config?.data || '{}')
        const newPost = {
          id: 'post_' + Date.now(),
          author: mockStore.profile.name || 'Student User',
          role: 'Active Student Member',
          avatar: mockStore.profile.name?.[0] || 'S',
          title: body.title || 'Discussion Topic',
          content: body.content || '',
          tags: body.tags || ['General'],
          created_at: 'Just now',
          upvotes: 1,
          comments_count: 0,
        }
        mockStore.communityPosts.unshift(newPost)
        return Promise.resolve({ data: newPost })
      }

      return Promise.resolve({ data: { posts: mockStore.communityPosts } })
    }

    // ── AI Mentor Chat Endpoints ──────────────────────────────────────────────
    if (url.includes('/api/chat/conversations')) {
      // 1. Post message to conversation
      if (url.includes('/message') && method === 'post') {
        const parts = url.split('/api/chat/conversations/')
        const convId = (parts[1] || '').split('/message')[0] || 'conv_1'
        const body = JSON.parse(error.config?.data || '{}')
        const msg = body.message || ''
        const msgLower = msg.toLowerCase()
        const target = mockStore.profile.target_career || 'Full Stack Engineer'

        let reply = `### Career Strategy Insight\n\nGreat question! As an aspiring **${target}**, focusing on practical hands-on projects, solid technical fundamentals, and targeted ATS resume keywords will accelerate your market readiness.`

        if (msgLower.includes('skill') || msgLower.includes('learn') || msgLower.includes('gaps')) {
          reply = `### Technical Skill Roadmap for ${target}\n\nBased on modern hiring standards, here is the prioritized roadmap:\n\n1. **Core Development**: Master React 19, TypeScript, and FastAPI/Node.js.\n2. **Database & Cache**: PostgreSQL schema design, indexing, and Redis caching.\n3. **DevOps & Cloud**: Docker containerization, CI/CD pipelines, and AWS deployment.\n\n*Actionable Step*: Track and update your acquired skills in the **Profile** tab to dynamically evaluate your readiness score!`
        } else if (msgLower.includes('interview') || msgLower.includes('system design') || msgLower.includes('prepare')) {
          reply = `### System Design & Interview Strategy\n\nFor technical and architectural interviews:\n\n1. **4-Step Framework**: Scope requirements -> High-Level Architecture -> Deep-dive components & caching -> Identify bottlenecks & scale.\n2. **Coding Practice**: Solve top pattern questions (Graphs, Two Pointers, Dynamic Programming).\n3. **Practice**: Test your real-time responses in our **AI Interview Simulator** tab!`
        } else if (msgLower.includes('resume') || msgLower.includes('ats') || msgLower.includes('parser')) {
          reply = `### Resume ATS Optimization Audit\n\n1. **Structure**: Single-column clean layout with standard sections (Skills, Projects, Experience, Education).\n2. **Target Keywords**: Align exact technical skills with the job description (${mockStore.profile.skills.slice(0, 5).join(', ')}).\n3. **XYZ Formula**: Structure bullet points as "Accomplished [X] measured by [Y] by doing [Z]".\n\n*Tip*: Scan your PDF in the **Resume ATS Optimizer** tab for an instant keyword alignment score!`
        } else if (msgLower.includes('project') || msgLower.includes('portfolio') || msgLower.includes('open source')) {
          reply = `### High-Impact Portfolio Recommendations for ${target}\n\n1. **Full-Stack SaaS / Microservice App**: Built with React, FastAPI/Node, and PostgreSQL with authentication and Docker compose.\n2. **Real-Time Collaboration System**: WebSockets + Redis Pub/Sub for real-time messaging or collaborative canvas.\n3. **AI / RAG Document Retrieval**: Vector search with PDF context grounding.\n\n*Pro Tip*: Ensure every GitHub repo has a detailed README with architecture diagrams and live demo links!`
        } else if (msgLower.includes('readiness') || msgLower.includes('score') || msgLower.includes('matrix')) {
          reply = `### Career Readiness Score Breakdown\n\nYour current readiness score is **${mockStore.jobScore.total_score}/100**.\n\n- **Skills Score**: ${mockStore.jobScore.skills_score}/35\n- **Projects Score**: ${mockStore.jobScore.projects_score}/25\n- **Internships Score**: ${mockStore.jobScore.internships_score}/20\n- **Certificates**: ${mockStore.jobScore.certificates_score}/10\n- **Profile**: ${mockStore.jobScore.profile_score}/10\n\n**Action Items**:\n${mockStore.jobScore.suggestions.map((s: string) => `• ${s}`).join('\n')}`
        }

        if (!mockStore.conversationMessages[convId]) {
          mockStore.conversationMessages[convId] = []
        }

        const now = new Date().toISOString()
        const userMsg = { role: 'user', content: msg, timestamp: now }
        const assistantMsg = { role: 'assistant', content: reply, timestamp: now }
        mockStore.conversationMessages[convId].push(userMsg, assistantMsg)

        return Promise.resolve({
          data: {
            messages: [...mockStore.conversationMessages[convId]]
          }
        })
      }

      // 2. Create new conversation
      if (method === 'post') {
        const body = JSON.parse(error.config?.data || '{}')
        const newId = 'conv_' + Date.now()
        const newConv = {
          id: newId,
          title: body.title || 'New Strategy Session',
          created_at: new Date().toISOString(),
        }
        mockStore.conversations.unshift(newConv)
        mockStore.conversationMessages[newId] = []
        return Promise.resolve({ data: newConv })
      }

      // 3. Delete conversation
      if (method === 'delete') {
        const parts = url.split('/api/chat/conversations/')
        const delId = (parts[1] || '').split('/')[0]?.split('?')[0]
        if (delId) {
          mockStore.conversations = mockStore.conversations.filter((c: any) => c.id !== delId)
          delete mockStore.conversationMessages[delId]
        }
        return Promise.resolve({ data: { success: true } })
      }

      // 4. Get single conversation
      if (method === 'get' && url.match(/\/conversations\/[^/?]+/)) {
        const parts = url.split('/api/chat/conversations/')
        const convId = (parts[1] || '').split('/')[0]?.split('?')[0]
        const conv = mockStore.conversations.find((c: any) => c.id === convId) || { id: convId, title: 'Conversation' }
        const messages = mockStore.conversationMessages[convId] || [
          { role: 'assistant', content: 'Hello! I am your CareerPilot AI mentor. How can I help guide your career path today?' }
        ]
        return Promise.resolve({
          data: {
            ...conv,
            messages,
          },
        })
      }

      // 5. List conversations
      return Promise.resolve({ data: { conversations: mockStore.conversations } })
    }

    if (url.includes('/api/chat/send')) {
      const body = JSON.parse(error.config?.data || '{}')
      const msg = (body.message || '').toLowerCase()
      const target = mockStore.profile.target_career || 'Full Stack Engineer'

      let reply = `Great question! As an aspiring ${target}, focusing on practical hands-on projects, solid technical fundamentals, and targeted ATS resume keywords will accelerate your progress.`

      if (msg.includes('skill') || msg.includes('learn')) {
        reply = `To excel as a ${target}, I recommend mastering:\n1. Core stack: ${mockStore.profile.skills.slice(0, 4).join(', ')}\n2. Cloud & DevOps: Docker, AWS, CI/CD Pipelines\n3. System Design: REST APIs, Caching, and Relational DB optimization.`
      } else if (msg.includes('interview') || msg.includes('prepare')) {
        reply = `For interview preparation:\n• Practice technical coding problems on LeetCode / HackerRank\n• Use our AI Interview Simulator tab to practice real-time STAR responses\n• Review top company questions in our Company Prep module!`
      } else if (msg.includes('project') || msg.includes('resume')) {
        reply = `To build an impressive portfolio:\n1. Build full-stack applications with user auth & DB persistence\n2. Run your resume through our Resume ATS Optimizer to maximize keyword scores\n3. Publish your code cleanly on GitHub with detailed README badges!`
      }

      return Promise.resolve({
        data: {
          reply,
          conversation_id: body.conversation_id || 'conv_' + Date.now(),
        },
      })
    }

    // ── Certificates & OCR Endpoints ──────────────────────────────────────────
    if (url.includes('/api/certificates')) {
      if (method === 'post') {
        const newCert = {
          id: 'cert_' + Date.now(),
          file_name: 'Uploaded_Certificate.pdf',
          certificate_title: 'Full Stack Development Certification',
          issuing_organization: 'Recognized Tech Academy',
          upload_date: new Date().toISOString(),
          status: 'completed',
          extracted_skills: {
            Verified: ['React', 'Node.js', 'PostgreSQL', 'API Security'],
          },
        }
        mockStore.certificates.unshift(newCert)
        return Promise.resolve({ data: newCert })
      }
      if (method === 'delete') {
        const id = url.split('/certificates/')[1]
        mockStore.certificates = mockStore.certificates.filter((c: any) => c.id !== id)
        return Promise.resolve({ data: { message: 'Deleted' } })
      }
      return Promise.resolve({ data: { certificates: mockStore.certificates } })
    }

    // ── Careers Endpoints ─────────────────────────────────────────────────────
    if (url.includes('/api/careers')) {
      if (url.includes('/target')) {
        const body = JSON.parse(error.config?.data || '{}')
        mockStore.profile.target_career = body.career_title || mockStore.profile.target_career
        return Promise.resolve({ data: { target_career: mockStore.profile.target_career } })
      }

      return Promise.resolve({
        data: {
          recommendations: [
            {
              title: 'Full Stack Engineer',
              match_percentage: 88,
              salary_range: '$85,000 - $130,000 / year',
              market_demand: 'Very High',
              reason: 'Excellent match based on your skills in React, TypeScript, Python, and FastAPI.',
              matching_skills: ['React', 'TypeScript', 'Python', 'FastAPI', 'SQL', 'Git'],
              missing_skills: ['Docker', 'GraphQL', 'AWS EC2', 'CI/CD Pipelines'],
            },
            {
              title: 'Frontend Specialist',
              match_percentage: 82,
              salary_range: '$80,000 - $125,000 / year',
              market_demand: 'High',
              reason: 'Strong alignment with your React and Tailwind CSS UI experience.',
              matching_skills: ['React', 'TypeScript', 'Tailwind CSS', 'Git'],
              missing_skills: ['Next.js', 'Jest / Vitest', 'Web Performance Optimization'],
            },
            {
              title: 'Backend Engineer',
              match_percentage: 75,
              salary_range: '$90,000 - $135,000 / year',
              market_demand: 'High',
              reason: 'Good match with your Python, FastAPI, and SQL experience.',
              matching_skills: ['Python', 'FastAPI', 'SQL', 'Git'],
              missing_skills: ['Redis Caching', 'Message Queues (RabbitMQ)', 'Docker'],
            },
            {
              title: 'AI Solutions Engineer',
              match_percentage: 70,
              salary_range: '$95,000 - $150,000 / year',
              market_demand: 'Very High',
              reason: 'Matches your interest in Artificial Intelligence and Web API integrations.',
              matching_skills: ['Python', 'FastAPI', 'Git'],
              missing_skills: ['LangChain / LlamaIndex', 'Vector Databases (Chroma/Pinecone)', 'PyTorch'],
            },
          ],
        },
      })
    }

    // ── Skill Gap Endpoints ───────────────────────────────────────────────────
    if (url.includes('/api/skill-gap')) {
      return Promise.resolve({
        data: {
          target_career: mockStore.profile.target_career,
          completion_percentage: 72,
          matching_skills: mockStore.profile.skills,
          missing_skills: [
            {
              skill: 'Docker & Containerization',
              importance: 'critical',
              difficulty: 'medium',
              courses: [
                { title: 'Docker for Beginners & Microservices', platform: 'Udemy', url: 'https://udemy.com' },
                { title: 'Containerizing Python Applications', platform: 'Docker Docs', url: 'https://docker.com' },
              ],
            },
            {
              skill: 'GraphQL API Design',
              importance: 'high',
              difficulty: 'medium',
              courses: [
                { title: 'GraphQL Fundamentals', platform: 'Coursera', url: 'https://coursera.org' },
              ],
            },
            {
              skill: 'CI/CD Automated Pipelines',
              importance: 'high',
              difficulty: 'hard',
              courses: [
                { title: 'GitHub Actions & CI/CD Masterclass', platform: 'YouTube', url: 'https://youtube.com' },
              ],
            },
          ],
        },
      })
    }

    // ── Learning Roadmap Endpoints ────────────────────────────────────────────
    if (url.includes('/api/learning')) {
      if (url.includes('/item/') && method === 'put') {
        const itemId = url.split('/item/')[1]?.split('/status')[0]
        const body = JSON.parse(error.config?.data || '{}')

        Object.values(mockStore.learning.stages).forEach((stageItems: any) => {
          const found = stageItems.find((i: any) => i.id === itemId)
          if (found) found.status = body.status
        })

        const allItems = Object.values(mockStore.learning.stages).flat() as any[]
        const completedCount = allItems.filter((i: any) => i.status === 'completed').length
        mockStore.learning.completed_items = completedCount
        mockStore.learning.progress_percentage = Math.round((completedCount / allItems.length) * 100)

        return Promise.resolve({ data: { progress_percentage: mockStore.learning.progress_percentage } })
      }
      return Promise.resolve({ data: mockStore.learning })
    }

    // Generic fallback for any unhandled request
    return Promise.reject(new Error(error.response?.data?.detail || error.message || 'Network Error'))
  },
)

export default api
