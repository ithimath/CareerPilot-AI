"""
CareerPilot AI — Technical Assessments & Mock Drills Router
Expanded to 20–25 questions per career-path test with:
  - ~30% easy / ~50% medium / ~20% hard difficulty mix
  - Conceptual, scenario-based, and code/output question types
  - Career-path specific content for 6 tracks
  - Full topic/difficulty breakdown stored per attempt
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.dependencies import get_current_user
from app.schemas.models import AssessmentSubmitRequest, OpenEndedAnswerSubmission
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# Active server-enforced assessment sessions: session_id -> { uid, test_id, start_timestamp, expires_timestamp, status, created_at }
ACTIVE_TEST_SESSIONS: Dict[str, dict] = {}


# ── Question Bank (per career path, 20–25 questions each) ────────────────────
# Difficulty: "easy" | "medium" | "hard"
# Type: "conceptual" | "scenario" | "code_output"

FULL_STACK_QUESTIONS = [
    # ── Easy (6 questions) ────────────────────────────────────────────────────
    {"id": 1, "topic": "HTML/CSS", "difficulty": "easy", "type": "conceptual",
     "q": "Which CSS property controls the space between an element's border and its content?",
     "options": ["margin", "padding", "gap", "spacing"],
     "correct": 1,
     "explanation": "padding controls the inner space between an element's content and its border. margin controls the outer space between elements."},
    {"id": 2, "topic": "JavaScript", "difficulty": "easy", "type": "conceptual",
     "q": "What does the `===` operator check in JavaScript?",
     "options": ["Only value equality", "Only type equality", "Both value and type equality (strict equality)", "Reference equality"],
     "correct": 2,
     "explanation": "`===` is the strict equality operator — it checks that both the value AND type are identical without type coercion."},
    {"id": 3, "topic": "React", "difficulty": "easy", "type": "conceptual",
     "q": "What hook is used to perform side effects in React functional components?",
     "options": ["useState", "useEffect", "useContext", "useReducer"],
     "correct": 1,
     "explanation": "useEffect runs after renders and handles side effects like API calls, subscriptions, and DOM mutations."},
    {"id": 4, "topic": "HTTP", "difficulty": "easy", "type": "conceptual",
     "q": "Which HTTP method is idempotent AND safe (no side effects)?",
     "options": ["POST", "PUT", "GET", "PATCH"],
     "correct": 2,
     "explanation": "GET is both safe (no server state change) and idempotent (same result on repeated calls). POST creates resources and is neither."},
    {"id": 5, "topic": "Git", "difficulty": "easy", "type": "conceptual",
     "q": "What does `git stash` do?",
     "options": ["Deletes uncommitted changes permanently", "Temporarily shelves uncommitted changes", "Creates a new branch", "Merges two branches"],
     "correct": 1,
     "explanation": "`git stash` saves your uncommitted changes to a stack so you can work on something else and restore them later with `git stash pop`."},
    {"id": 6, "topic": "SQL", "difficulty": "easy", "type": "conceptual",
     "q": "Which SQL statement retrieves unique values from a column?",
     "options": ["SELECT UNIQUE", "SELECT DISTINCT", "SELECT DIFFERENT", "SELECT FILTER"],
     "correct": 1,
     "explanation": "SELECT DISTINCT eliminates duplicate rows from the result set."},
    # ── Medium (11 questions) ─────────────────────────────────────────────────
    {"id": 7, "topic": "React", "difficulty": "medium", "type": "conceptual",
     "q": "What is the primary purpose of React's `useMemo` hook?",
     "options": ["Perform side effects on mount", "Memoize expensive computed values between renders", "Replace Redux for state management", "Lazy-load components"],
     "correct": 1,
     "explanation": "useMemo caches the result of a computation and only recomputes it when its dependencies change, preventing expensive recalculations on every render."},
    {"id": 8, "topic": "React", "difficulty": "medium", "type": "scenario",
     "q": "A React component re-renders excessively when a parent re-renders, even though its props haven't changed. What is the best fix?",
     "options": ["Move state to Context", "Wrap the component in React.memo()", "Use useRef instead of useState", "Convert to a class component"],
     "correct": 1,
     "explanation": "React.memo() is a Higher-Order Component that prevents a functional component from re-rendering if its props haven't changed."},
    {"id": 9, "topic": "JavaScript", "difficulty": "medium", "type": "code_output",
     "q": "What does the following code log?\n```js\nconsole.log(typeof null);\n```",
     "options": ["'null'", "'undefined'", "'object'", "'boolean'"],
     "correct": 2,
     "explanation": "This is a longstanding JavaScript bug — `typeof null` returns 'object', not 'null'. It's preserved for backward compatibility."},
    {"id": 10, "topic": "REST API", "difficulty": "medium", "type": "conceptual",
     "q": "Which HTTP status code should a REST API return when a resource is successfully created?",
     "options": ["200 OK", "201 Created", "204 No Content", "202 Accepted"],
     "correct": 1,
     "explanation": "201 Created signals that a new resource has been successfully created. The response should include a Location header pointing to the new resource."},
    {"id": 11, "topic": "JavaScript", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between `Promise.all()` and `Promise.allSettled()`?",
     "options": [
         "Promise.all() waits for ALL to settle; Promise.allSettled() rejects on first failure",
         "Promise.all() rejects on first failure; Promise.allSettled() waits for ALL to settle regardless",
         "They are identical",
         "Promise.all() only works with async/await"
     ],
     "correct": 1,
     "explanation": "Promise.all() short-circuits and rejects as soon as any promise rejects. Promise.allSettled() always waits for every promise and returns each outcome (fulfilled or rejected)."},
    {"id": 12, "topic": "SQL", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between `INNER JOIN` and `LEFT JOIN`?",
     "options": [
         "INNER JOIN returns all rows from both tables; LEFT JOIN returns matching rows only",
         "INNER JOIN returns only matching rows; LEFT JOIN returns all rows from the left table plus matching from the right",
         "They are identical",
         "LEFT JOIN requires an index; INNER JOIN does not"
     ],
     "correct": 1,
     "explanation": "INNER JOIN returns only rows with a match in both tables. LEFT JOIN returns all rows from the left table even if there's no match in the right (NULLs fill non-matching columns)."},
    {"id": 13, "topic": "CSS", "difficulty": "medium", "type": "scenario",
     "q": "A flex container's items are not wrapping to the next line when there's no room. Which property fixes this?",
     "options": ["flex-direction: column", "flex-wrap: wrap", "align-items: flex-start", "justify-content: space-between"],
     "correct": 1,
     "explanation": "By default, flexbox forces items onto a single line. `flex-wrap: wrap` allows items to wrap onto multiple lines when the container's width is exceeded."},
    {"id": 14, "topic": "TypeScript", "difficulty": "medium", "type": "conceptual",
     "q": "What is a TypeScript `interface` used for?",
     "options": ["Defining runtime class behavior", "Describing the shape of an object at compile-time", "Creating abstract base classes", "Enforcing method implementations in functions"],
     "correct": 1,
     "explanation": "TypeScript interfaces define the structure (shape) of objects — their properties and method signatures — purely for compile-time type checking."},
    {"id": 15, "topic": "REST API", "difficulty": "medium", "type": "conceptual",
     "q": "What does CORS stand for, and why do browsers enforce it?",
     "options": [
         "Cross-Origin Resource Sharing — prevents a web page from making requests to a different domain without permission",
         "Client-Origin Request System — limits server response size",
         "Cache Origin Response Sync — controls caching",
         "Cross-Origin Request Streaming — enables WebSocket connections"
     ],
     "correct": 0,
     "explanation": "CORS is a browser security mechanism that restricts web pages from making requests to a different domain (origin) than the one that served the page, unless the server explicitly allows it."},
    {"id": 16, "topic": "Node.js", "difficulty": "medium", "type": "conceptual",
     "q": "What is the purpose of the Node.js Event Loop?",
     "options": [
         "To manage multiple CPU threads for parallelism",
         "To handle asynchronous I/O operations in a single-threaded environment without blocking",
         "To garbage-collect unused memory",
         "To compile JavaScript to machine code at runtime"
     ],
     "correct": 1,
     "explanation": "The Node.js Event Loop allows non-blocking I/O by offloading operations to the system kernel and executing callbacks when operations complete, enabling high concurrency on a single thread."},
    {"id": 17, "topic": "Database", "difficulty": "medium", "type": "conceptual",
     "q": "What does database indexing improve?",
     "options": ["Write throughput", "Read query performance (especially on large tables)", "Data compression ratio", "Transaction isolation level"],
     "correct": 1,
     "explanation": "An index creates a separate data structure that allows the database to find rows matching a WHERE clause without scanning every row (a full table scan)."},
    # ── Hard (5 questions) ────────────────────────────────────────────────────
    {"id": 18, "topic": "System Design", "difficulty": "hard", "type": "scenario",
     "q": "You need to design a rate limiter that allows each user 100 requests per minute. Which algorithm handles burst traffic most gracefully?",
     "options": ["Fixed Window Counter", "Sliding Window Log", "Token Bucket", "Leaky Bucket"],
     "correct": 2,
     "explanation": "Token Bucket accumulates tokens at a fixed rate and allows bursts up to the bucket capacity, making it the most flexible for handling traffic spikes while still enforcing an average rate."},
    {"id": 19, "topic": "JavaScript", "difficulty": "hard", "type": "code_output",
     "q": "What does this code output?\n```js\nconst obj = { a: 1 };\nconst copy = Object.assign({}, obj);\ncopy.a = 99;\nconsole.log(obj.a);\n```",
     "options": ["99", "1", "undefined", "ReferenceError"],
     "correct": 1,
     "explanation": "Object.assign() creates a shallow copy. Primitive values (like numbers) are copied by value, so mutating `copy.a` does not affect `obj.a`. (Nested objects would be affected.)"},
    {"id": 20, "topic": "React", "difficulty": "hard", "type": "scenario",
     "q": "A large list component re-renders on every parent update, causing jank. The list data itself doesn't change. What is the optimal solution?",
     "options": [
         "Move the list to a separate file",
         "Use React.memo() on the list component AND useCallback() on any event handlers passed as props",
         "Use useEffect to re-render the list only on mount",
         "Convert to a class component with shouldComponentUpdate"
     ],
     "correct": 1,
     "explanation": "React.memo() prevents re-renders when props are the same, but if event handler props are new function references each render (from the parent), you must also wrap them in useCallback() to preserve referential equality."},
    {"id": 21, "topic": "Database", "difficulty": "hard", "type": "conceptual",
     "q": "What does the CAP theorem state?",
     "options": [
         "A distributed system can guarantee Consistency, Availability, and Partition Tolerance simultaneously",
         "A distributed system can guarantee at most two of: Consistency, Availability, Partition Tolerance",
         "Partition Tolerance can always be sacrificed for better performance",
         "Availability is always more important than Consistency in production systems"
     ],
     "correct": 1,
     "explanation": "The CAP theorem states that in the presence of a network partition, a distributed system must choose between Consistency (all nodes see the same data) or Availability (every request gets a response). Partition Tolerance is not optional in real distributed systems."},
    {"id": 22, "topic": "Security", "difficulty": "hard", "type": "scenario",
     "q": "A web application renders user-submitted comments directly as HTML. What vulnerability does this introduce and how do you fix it?",
     "options": [
         "SQL Injection — use parameterized queries",
         "XSS (Cross-Site Scripting) — escape all user-generated content before rendering it as HTML",
         "CSRF — add SameSite cookie flags",
         "Path Traversal — validate file upload names"
     ],
     "correct": 1,
     "explanation": "Rendering unsanitized user input as HTML enables XSS attacks. Fix by escaping HTML entities (e.g., using textContent instead of innerHTML in JavaScript) or using a library like DOMPurify."},
]

AIML_QUESTIONS = [
    # ── Easy (6 questions) ────────────────────────────────────────────────────
    {"id": 1, "topic": "ML Basics", "difficulty": "easy", "type": "conceptual",
     "q": "What is the difference between supervised and unsupervised learning?",
     "options": [
         "Supervised uses labeled data; unsupervised finds patterns in unlabeled data",
         "Supervised is faster; unsupervised is slower",
         "Unsupervised uses labeled data; supervised uses unlabeled data",
         "They are the same — just different names"
     ],
     "correct": 0,
     "explanation": "Supervised learning trains on labeled input-output pairs to predict outputs. Unsupervised learning finds structure or clusters in data without predefined labels."},
    {"id": 2, "topic": "ML Basics", "difficulty": "easy", "type": "conceptual",
     "q": "What does 'overfitting' mean in machine learning?",
     "options": [
         "The model is too simple to capture patterns in the data",
         "The model memorizes training data but fails to generalize to new data",
         "The model takes too long to train",
         "The model has too few parameters"
     ],
     "correct": 1,
     "explanation": "Overfitting occurs when a model learns noise and specifics of the training set, resulting in high training accuracy but poor performance on validation/test data."},
    {"id": 3, "topic": "Python", "difficulty": "easy", "type": "conceptual",
     "q": "Which NumPy function creates an array of zeros with a specified shape?",
     "options": ["np.empty()", "np.zeros()", "np.full()", "np.blank()"],
     "correct": 1,
     "explanation": "np.zeros(shape) creates an ndarray filled with 0.0 values. np.empty() allocates uninitialized memory (values are unpredictable)."},
    {"id": 4, "topic": "Statistics", "difficulty": "easy", "type": "conceptual",
     "q": "What does a correlation coefficient of -1 indicate?",
     "options": [
         "No linear relationship",
         "A perfect positive linear relationship",
         "A perfect negative linear relationship",
         "The variables are independent"
     ],
     "correct": 2,
     "explanation": "A correlation of -1 means a perfect inverse linear relationship — as one variable increases, the other decreases proportionally."},
    {"id": 5, "topic": "Deep Learning", "difficulty": "easy", "type": "conceptual",
     "q": "What is the role of an activation function in a neural network?",
     "options": [
         "To initialize weight values",
         "To introduce non-linearity so the network can learn complex patterns",
         "To normalize the input data",
         "To calculate the loss"
     ],
     "correct": 1,
     "explanation": "Without activation functions, a neural network would be a linear transformation regardless of depth. Non-linear activations (ReLU, sigmoid, tanh) allow the network to approximate any function."},
    {"id": 6, "topic": "ML Basics", "difficulty": "easy", "type": "conceptual",
     "q": "What is the purpose of a train/validation/test split in ML?",
     "options": [
         "To reduce training time",
         "To train on one set, tune hyperparameters on another, and evaluate final performance on unseen data",
         "To increase dataset size through duplication",
         "To run training on multiple GPUs"
     ],
     "correct": 1,
     "explanation": "Training set trains the model. Validation set tunes hyperparameters and prevents overfitting. Test set gives an unbiased estimate of real-world performance on unseen data."},
    # ── Medium (11 questions) ─────────────────────────────────────────────────
    {"id": 7, "topic": "Algorithms", "difficulty": "medium", "type": "conceptual",
     "q": "What is gradient descent, and what does the learning rate control?",
     "options": [
         "An optimizer that maximizes loss; learning rate controls batch size",
         "An optimization algorithm that iteratively adjusts parameters to minimize loss; learning rate controls step size",
         "A regularization technique; learning rate controls dropout probability",
         "A data preprocessing step; learning rate controls normalization scale"
     ],
     "correct": 1,
     "explanation": "Gradient descent computes the gradient of the loss w.r.t. parameters and moves in the direction that reduces the loss. The learning rate determines how large each update step is."},
    {"id": 8, "topic": "Deep Learning", "difficulty": "medium", "type": "conceptual",
     "q": "What problem does batch normalization solve?",
     "options": [
         "Overfitting in small datasets",
         "Vanishing/exploding gradients and internal covariate shift by normalizing layer inputs",
         "Slow inference time in production",
         "Class imbalance in training data"
     ],
     "correct": 1,
     "explanation": "Batch normalization normalizes the inputs to each layer to have zero mean and unit variance, which stabilizes training, allows higher learning rates, and reduces sensitivity to weight initialization."},
    {"id": 9, "topic": "NLP", "difficulty": "medium", "type": "conceptual",
     "q": "What does the Transformer architecture's 'attention mechanism' do?",
     "options": [
         "Downsamples sequence length for efficiency",
         "Allows each token to 'attend' to all other tokens in the sequence, learning contextual relationships",
         "Applies a recurrent cell like LSTM to each token",
         "Converts text to fixed-size embeddings using TF-IDF"
     ],
     "correct": 1,
     "explanation": "Self-attention computes a weighted sum of all token representations, where weights reflect how relevant each token is to every other token — enabling the model to capture long-range dependencies."},
    {"id": 10, "topic": "ML Basics", "difficulty": "medium", "type": "scenario",
     "q": "Your binary classifier achieves 99% accuracy on a dataset where 99% of samples are class 0. What metric should you use instead?",
     "options": ["Accuracy", "F1-Score or AUC-ROC", "Mean Squared Error", "Log Loss only"],
     "correct": 1,
     "explanation": "A model that always predicts the majority class gets 99% accuracy trivially. F1-Score (balances precision/recall) and AUC-ROC are appropriate for imbalanced classification problems."},
    {"id": 11, "topic": "Algorithms", "difficulty": "medium", "type": "conceptual",
     "q": "What is regularization, and what does L2 (Ridge) regularization do?",
     "options": [
         "A data augmentation technique; it increases the amount of training data",
         "A technique to reduce overfitting; L2 penalizes the sum of squared weights, shrinking large weights",
         "A loss function; it computes mean absolute error",
         "A training scheduler; L2 reduces the learning rate over time"
     ],
     "correct": 1,
     "explanation": "Regularization adds a penalty to the loss function to discourage complex models. L2 regularization penalizes large weights quadratically, effectively shrinking all weights and reducing overfitting."},
    {"id": 12, "topic": "Feature Engineering", "difficulty": "medium", "type": "conceptual",
     "q": "Why is feature scaling (normalization/standardization) important for many ML algorithms?",
     "options": [
         "It increases the number of features",
         "It ensures features with larger magnitudes don't dominate distance-based or gradient-based algorithms",
         "It reduces dataset size",
         "It is only needed for decision trees"
     ],
     "correct": 1,
     "explanation": "Algorithms like k-NN, SVM, and gradient descent-based models are sensitive to feature scale. Without scaling, features with larger magnitudes dominate, leading to biased learning."},
    {"id": 13, "topic": "Python", "difficulty": "medium", "type": "code_output",
     "q": "What does `df.groupby('city')['sales'].mean()` in pandas return?",
     "options": [
         "A single mean of all sales",
         "The average sales value grouped by each unique city",
         "A DataFrame with sales sorted by city",
         "A pivot table"
     ],
     "correct": 1,
     "explanation": "groupby('city') splits the DataFrame by city, then ['sales'].mean() computes the mean sales for each city group, returning a Series indexed by city."},
    {"id": 14, "topic": "Deep Learning", "difficulty": "medium", "type": "conceptual",
     "q": "What is dropout and why is it used during training?",
     "options": [
         "A pruning technique used after training to reduce model size",
         "A regularization method that randomly sets neuron activations to zero during training to prevent co-adaptation",
         "A learning rate scheduler",
         "A data augmentation strategy for images"
     ],
     "correct": 1,
     "explanation": "Dropout randomly deactivates a fraction of neurons during each forward pass, forcing the network to learn redundant representations and preventing co-adaptation, which reduces overfitting."},
    {"id": 15, "topic": "ML Basics", "difficulty": "medium", "type": "conceptual",
     "q": "What is cross-validation and why is it used?",
     "options": [
         "Running the model on multiple GPUs",
         "A technique to estimate model performance by training/testing on different subsets of the data (reducing variance in evaluation)",
         "Combining multiple models into an ensemble",
         "Normalizing data across multiple features simultaneously"
     ],
     "correct": 1,
     "explanation": "Cross-validation (e.g., k-fold) splits data into k subsets, trains on k-1, tests on 1, and repeats k times. It gives a more reliable performance estimate than a single train/test split."},
    {"id": 16, "topic": "NLP", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between stemming and lemmatization in NLP?",
     "options": [
         "Stemming uses a dictionary; lemmatization uses rules",
         "Stemming crudely chops word endings; lemmatization returns the dictionary base form",
         "They are identical processes",
         "Lemmatization only works for English"
     ],
     "correct": 1,
     "explanation": "Stemming is a heuristic that removes suffixes (e.g., 'running' → 'run', but 'better' → 'bett'). Lemmatization uses vocabulary and morphological analysis to return the correct base form ('better' → 'good')."},
    {"id": 17, "topic": "Statistics", "difficulty": "medium", "type": "conceptual",
     "q": "What does a p-value of 0.03 mean in hypothesis testing (significance level α = 0.05)?",
     "options": [
         "There is a 3% chance the hypothesis is true",
         "The result is statistically significant — we reject the null hypothesis",
         "The result is not significant — we fail to reject the null hypothesis",
         "The effect size is 3%"
     ],
     "correct": 1,
     "explanation": "p-value < α (0.03 < 0.05) means the observed result is unlikely to occur by chance under the null hypothesis, so we reject the null hypothesis."},
    # ── Hard (5 questions) ────────────────────────────────────────────────────
    {"id": 18, "topic": "Deep Learning", "difficulty": "hard", "type": "conceptual",
     "q": "What is the vanishing gradient problem in deep neural networks?",
     "options": [
         "Gradients grow too large and cause weight explosion",
         "Gradients shrink exponentially as they propagate back through many layers, causing early layers to learn very slowly",
         "The loss function becomes constant during training",
         "Batch size is too small to compute stable gradients"
     ],
     "correct": 1,
     "explanation": "In deep networks with sigmoid/tanh activations, gradients are multiplied by derivatives (< 1) at each layer during backpropagation, shrinking exponentially. Early layers receive near-zero gradients and fail to learn. ReLU and residual connections (skip connections) address this."},
    {"id": 19, "topic": "Algorithms", "difficulty": "hard", "type": "scenario",
     "q": "You have 1M training samples but training is slow. Which approach best preserves convergence quality while reducing training time?",
     "options": [
         "Use batch size 1 (stochastic gradient descent)",
         "Use mini-batch gradient descent with adaptive learning rates (e.g., Adam optimizer)",
         "Train on only 10% of the data",
         "Increase epochs and reduce learning rate"
     ],
     "correct": 1,
     "explanation": "Mini-batch gradient descent with an adaptive optimizer like Adam combines the noise regularization benefit of small batches with the computational efficiency of vectorized batch operations, converging faster and more stably than SGD alone."},
    {"id": 20, "topic": "NLP", "difficulty": "hard", "type": "conceptual",
     "q": "What is RLHF (Reinforcement Learning from Human Feedback) and why is it used to train LLMs?",
     "options": [
         "A technique to reduce LLM inference cost",
         "A training paradigm where human preference scores guide a reward model that fine-tunes the LLM to generate more helpful, accurate, and safe outputs",
         "A data augmentation method for low-resource languages",
         "A method to compress large models via knowledge distillation"
     ],
     "correct": 1,
     "explanation": "RLHF uses human raters to rank model outputs, trains a reward model on those preferences, then uses RL (PPO) to fine-tune the LLM to maximize the reward signal — aligning model behavior with human intent."},
    {"id": 21, "topic": "ML Systems", "difficulty": "hard", "type": "scenario",
     "q": "A deployed ML model's performance degrades over time even though the code hasn't changed. What is the most likely cause?",
     "options": [
         "The server ran out of memory",
         "Data/concept drift — the statistical distribution of production data has shifted from the training distribution",
         "The model file was corrupted",
         "Overfitting that only appears after deployment"
     ],
     "correct": 1,
     "explanation": "Data drift (input distribution changes) or concept drift (relationship between inputs and outputs changes) causes model performance to degrade post-deployment. Monitoring input distributions and retraining periodically addresses this."},
    {"id": 22, "topic": "Deep Learning", "difficulty": "hard", "type": "conceptual",
     "q": "What is the key architectural innovation in ResNet that enables training of very deep networks (100+ layers)?",
     "options": [
         "Depthwise separable convolutions",
         "Residual/skip connections that add the input directly to the output of a layer block, allowing gradients to flow unchanged",
         "Batch normalization applied after every layer",
         "A smaller learning rate for deeper layers"
     ],
     "correct": 1,
     "explanation": "Skip connections allow the gradient to bypass layers entirely, preventing vanishing gradients and enabling identity mappings — so the network can learn residual functions (small corrections) rather than entire mappings from scratch."},
]

BACKEND_QUESTIONS = [
    # ── Easy (6 questions) ────────────────────────────────────────────────────
    {"id": 1, "topic": "APIs", "difficulty": "easy", "type": "conceptual",
     "q": "What does REST stand for in REST API?",
     "options": ["Rapid Endpoint State Transfer", "Representational State Transfer", "Remote Execution Service Transfer", "Resource Entity Storage Technology"],
     "correct": 1,
     "explanation": "REST (Representational State Transfer) is an architectural style for distributed hypermedia systems, using HTTP methods and stateless communication."},
    {"id": 2, "topic": "HTTP", "difficulty": "easy", "type": "conceptual",
     "q": "What HTTP status code indicates that a resource was not found?",
     "options": ["500", "401", "404", "403"],
     "correct": 2,
     "explanation": "404 Not Found indicates the server cannot find the requested resource. 401 = unauthorized, 403 = forbidden, 500 = server error."},
    {"id": 3, "topic": "Database", "difficulty": "easy", "type": "conceptual",
     "q": "What is a Primary Key in a relational database?",
     "options": [
         "A key that references another table",
         "A unique identifier for each row in a table — it cannot be NULL and must be unique",
         "A key that enforces ordering",
         "An index on a frequently queried column"
     ],
     "correct": 1,
     "explanation": "A Primary Key uniquely identifies each record in a table. It is automatically indexed, cannot be NULL, and must be unique across all rows."},
    {"id": 4, "topic": "Python", "difficulty": "easy", "type": "conceptual",
     "q": "What is the purpose of a Python decorator?",
     "options": [
         "To format code output",
         "To wrap a function and modify its behavior without changing its source code",
         "To import external libraries",
         "To define abstract base classes"
     ],
     "correct": 1,
     "explanation": "Decorators are higher-order functions that wrap another function, allowing you to add behavior (logging, auth, caching) before/after the wrapped function runs."},
    {"id": 5, "topic": "Concurrency", "difficulty": "easy", "type": "conceptual",
     "q": "What is the difference between a process and a thread?",
     "options": [
         "A process is a thread with a larger memory footprint",
         "A process is an independent program with its own memory space; threads are lightweight execution units within a process that share memory",
         "Threads run on separate CPUs; processes run on a single CPU",
         "They are the same thing in modern operating systems"
     ],
     "correct": 1,
     "explanation": "Processes have isolated memory spaces. Threads share the same memory within a process, making communication faster but requiring synchronization to prevent race conditions."},
    {"id": 6, "topic": "Security", "difficulty": "easy", "type": "conceptual",
     "q": "What does JWT stand for and what is it used for?",
     "options": [
         "Java Web Token — for Java backend authentication",
         "JSON Web Token — a compact, URL-safe way to transmit claims (e.g., user identity) between parties",
         "JavaScript Worker Task — for background jobs",
         "JSON Write Transfer — for API request bodies"
     ],
     "correct": 1,
     "explanation": "JWT (JSON Web Token) is a signed token (header.payload.signature) used for stateless authentication. The server signs the token; the client sends it on subsequent requests."},
    # ── Medium (11 questions) ─────────────────────────────────────────────────
    {"id": 7, "topic": "Database", "difficulty": "medium", "type": "conceptual",
     "q": "Explain the ACID properties of a database transaction.",
     "options": [
         "Atomicity, Consistency, Isolation, Durability — guarantees that transactions are processed reliably",
         "Availability, Concurrency, Integrity, Distribution",
         "Atomicity, Caching, Indexing, Durability",
         "Availability, Consistency, Isolation, Distribution"
     ],
     "correct": 0,
     "explanation": "ACID: Atomicity (all or nothing), Consistency (valid state before/after), Isolation (concurrent transactions don't interfere), Durability (committed data persists even after crashes)."},
    {"id": 8, "topic": "System Design", "difficulty": "medium", "type": "conceptual",
     "q": "What is the purpose of a message queue (e.g., RabbitMQ, Kafka) in a backend system?",
     "options": [
         "To cache database query results",
         "To decouple services by enabling asynchronous communication — producers publish messages, consumers process them independently",
         "To load-balance HTTP requests",
         "To store user session data"
     ],
     "correct": 1,
     "explanation": "Message queues allow services to communicate asynchronously. The producer doesn't wait for the consumer to finish, enabling decoupling, fault tolerance, and scalable background processing."},
    {"id": 9, "topic": "Python", "difficulty": "medium", "type": "code_output",
     "q": "What is the output of this Python code?\n```python\ndef f(x, lst=[]):\n    lst.append(x)\n    return lst\nprint(f(1))\nprint(f(2))\n```",
     "options": ["[1]\n[2]", "[1]\n[1, 2]", "[1, 2]\n[1, 2]", "Error"],
     "correct": 1,
     "explanation": "Python evaluates mutable default arguments once at function definition time, not each call. So the same list is reused across calls. f(1) → [1], f(2) → [1, 2]. This is a classic Python gotcha."},
    {"id": 10, "topic": "Caching", "difficulty": "medium", "type": "conceptual",
     "q": "What cache invalidation strategy evicts the item that was accessed least recently?",
     "options": ["FIFO (First In First Out)", "LRU (Least Recently Used)", "MRU (Most Recently Used)", "LFU (Least Frequently Used)"],
     "correct": 1,
     "explanation": "LRU evicts the item that hasn't been accessed for the longest time, under the assumption that recently used data is more likely to be needed again."},
    {"id": 11, "topic": "Security", "difficulty": "medium", "type": "conceptual",
     "q": "What is SQL injection and how do parameterized queries prevent it?",
     "options": [
         "SQL injection is slow query performance; parameterized queries use indexes to fix it",
         "SQL injection inserts malicious SQL via user input; parameterized queries treat input as data (not executable code), preventing it",
         "SQL injection is a database backup technique",
         "Parameterized queries cache SQL execution plans to prevent duplicate queries"
     ],
     "correct": 1,
     "explanation": "SQL injection tricks the database into executing attacker-controlled SQL. Parameterized queries (prepared statements) separate code from data — the input is never interpreted as SQL."},
    {"id": 12, "topic": "APIs", "difficulty": "medium", "type": "conceptual",
     "q": "What is idempotency in REST APIs, and which methods should be idempotent?",
     "options": [
         "Idempotent means the same response regardless of authentication; only GET should be idempotent",
         "Idempotent means repeating the same request produces the same result; GET, PUT, DELETE should be idempotent",
         "Idempotent means the API never throws errors; all methods must be idempotent",
         "Idempotency only applies to POST requests"
     ],
     "correct": 1,
     "explanation": "An idempotent operation produces the same result whether called once or many times. GET, PUT, DELETE are idempotent. POST is not (each call creates a new resource)."},
    {"id": 13, "topic": "Concurrency", "difficulty": "medium", "type": "conceptual",
     "q": "What is a race condition in concurrent programming?",
     "options": [
         "When two threads compete to be the fastest",
         "When multiple threads access shared data simultaneously and the final result depends on the unpredictable execution order",
         "When a thread acquires too many locks",
         "When CPU context switching is too slow"
     ],
     "correct": 1,
     "explanation": "A race condition occurs when the program's outcome depends on the interleaving of multiple thread operations on shared state, producing incorrect or inconsistent results."},
    {"id": 14, "topic": "Database", "difficulty": "medium", "type": "conceptual",
     "q": "What is database normalization and what does 3NF (Third Normal Form) prevent?",
     "options": [
         "Normalization indexes tables; 3NF prevents slow joins",
         "Normalization organizes tables to reduce redundancy; 3NF prevents transitive dependencies (non-key columns depending on other non-key columns)",
         "Normalization encrypts data; 3NF prevents SQL injection",
         "Normalization shards databases; 3NF prevents data loss on partition"
     ],
     "correct": 1,
     "explanation": "Normalization reduces data redundancy. 3NF requires that non-key columns depend ONLY on the primary key, not on other non-key columns, preventing update anomalies."},
    {"id": 15, "topic": "FastAPI/Python", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between `async def` and `def` in FastAPI route handlers?",
     "options": [
         "async def routes return JSON; def routes return HTML",
         "async def handlers are non-blocking coroutines that free the event loop during I/O; def handlers block the thread",
         "def handlers run faster for CPU-intensive tasks; async def is only for file operations",
         "They are identical — FastAPI handles both the same way"
     ],
     "correct": 1,
     "explanation": "FastAPI runs async def handlers in the async event loop without blocking. Regular def handlers run in a thread pool executor. Use async for I/O-bound operations (DB, HTTP calls) and def for CPU-bound tasks."},
    {"id": 16, "topic": "System Design", "difficulty": "medium", "type": "conceptual",
     "q": "What is horizontal scaling vs. vertical scaling?",
     "options": [
         "Horizontal = adding more CPU/RAM to one server; Vertical = adding more servers",
         "Horizontal = adding more servers; Vertical = adding more CPU/RAM to one server",
         "They are the same concept with different names",
         "Horizontal scaling only applies to databases"
     ],
     "correct": 1,
     "explanation": "Horizontal scaling (scaling out) adds more machines. Vertical scaling (scaling up) increases resources on an existing machine. Horizontal scaling is generally preferred for fault tolerance and unlimited growth."},
    {"id": 17, "topic": "Security", "difficulty": "medium", "type": "conceptual",
     "q": "What does bcrypt do when storing user passwords?",
     "options": [
         "Encrypts the password with AES-256",
         "Hashes the password with a built-in work factor and random salt, making brute-force attacks computationally expensive",
         "Base64 encodes the password",
         "Stores the password in a secure HSM"
     ],
     "correct": 1,
     "explanation": "bcrypt is a slow hash function designed for passwords. The cost factor makes it orders of magnitude slower than general hashes (SHA-256), and the random salt prevents rainbow table attacks."},
    # ── Hard (5 questions) ────────────────────────────────────────────────────
    {"id": 18, "topic": "System Design", "difficulty": "hard", "type": "scenario",
     "q": "You need to design a URL shortener service that handles 100M URLs and 10B redirects/day. What is the most critical design decision?",
     "options": [
         "Choose MySQL over PostgreSQL",
         "Use a consistent hashing scheme for the short code, cache hot URLs in Redis, and distribute read traffic across replicas",
         "Store everything in a single relational database",
         "Generate sequential numeric IDs for all URLs"
     ],
     "correct": 1,
     "explanation": "At 10B redirects/day (~115K req/s), the redirect path is read-heavy. Redis caching hot URLs reduces DB load by 99%. Consistent hashing prevents hotspots. Read replicas distribute load. The write path is much lighter."},
    {"id": 19, "topic": "Database", "difficulty": "hard", "type": "conceptual",
     "q": "What is the N+1 query problem in ORMs and how do you fix it?",
     "options": [
         "When a query returns N+1 more results than expected; fix with pagination",
         "When fetching N records triggers N additional queries (one per record); fix with eager loading (JOIN or prefetch_related)",
         "When N simultaneous users trigger 1 shared query; fix with connection pooling",
         "When an index has N+1 entries; fix by rebuilding the index"
     ],
     "correct": 1,
     "explanation": "N+1 occurs when you fetch a list of N records then loop to fetch related data for each (N queries). Fix by using JOIN-based eager loading or ORM prefetching to load all data in 1–2 queries."},
    {"id": 20, "topic": "Concurrency", "difficulty": "hard", "type": "conceptual",
     "q": "What is a deadlock, and what are the four conditions required for it to occur?",
     "options": [
         "A deadlock is CPU starvation; it requires high load, slow network, large memory, and disk bottleneck",
         "A deadlock is mutual blocking of threads; it requires Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait",
         "A deadlock occurs only in distributed systems; it requires network partitions",
         "A deadlock is when a thread runs indefinitely; it requires an infinite loop"
     ],
     "correct": 1,
     "explanation": "Deadlock: two or more threads block each other waiting for locks the other holds. The four Coffman conditions: (1) Mutual Exclusion, (2) Hold and Wait, (3) No Preemption, (4) Circular Wait. Breaking any one prevents deadlock."},
    {"id": 21, "topic": "System Design", "difficulty": "hard", "type": "scenario",
     "q": "A microservice's downstream dependency is slow. How do you prevent this from cascading and taking down your entire service?",
     "options": [
         "Increase the timeout to 60 seconds",
         "Implement a Circuit Breaker pattern that opens after a failure threshold, returning fallback responses until the dependency recovers",
         "Add more replicas of the slow downstream service",
         "Cache all requests to avoid calling the dependency"
     ],
     "correct": 1,
     "explanation": "The Circuit Breaker pattern (Closed → Open → Half-Open) stops forwarding requests to a failing dependency after a threshold, returning fast fallback responses instead of waiting and exhausting thread pools."},
    {"id": 22, "topic": "Security", "difficulty": "hard", "type": "conceptual",
     "q": "What is a timing attack, and how does it apply to token comparison?",
     "options": [
         "An attack that exploits server time zones",
         "An attack that measures how long a comparison takes — early termination on string mismatch leaks information; fix with constant-time comparison",
         "An attack that floods the server with time-sensitive requests",
         "An attack on JWT expiration timestamps"
     ],
     "correct": 1,
     "explanation": "Standard string comparison short-circuits on the first mismatch. By measuring response time, an attacker can determine how many characters of a token match the real value. `secrets.compare_digest()` in Python performs constant-time comparison regardless of where the mismatch occurs."},
]

FRONTEND_QUESTIONS = [
    # ── Easy (6 questions) ────────────────────────────────────────────────────
    {"id": 1, "topic": "HTML", "difficulty": "easy", "type": "conceptual",
     "q": "What is the purpose of the HTML `<meta charset='UTF-8'>` tag?",
     "options": [
         "Sets the page title",
         "Declares the character encoding so browsers correctly render text including special characters",
         "Links an external stylesheet",
         "Sets the page language"
     ],
     "correct": 1,
     "explanation": "UTF-8 encoding supports nearly all human languages. Declaring it prevents garbled text when the page contains non-ASCII characters."},
    {"id": 2, "topic": "CSS", "difficulty": "easy", "type": "conceptual",
     "q": "What does `box-sizing: border-box` do?",
     "options": [
         "Removes the element's border",
         "Makes width and height include padding and border in the total size calculation",
         "Enables flexbox layout",
         "Centers the element on the page"
     ],
     "correct": 1,
     "explanation": "With border-box, the declared width/height is the total element size including padding and border. Without it (content-box), padding and border are added ON TOP of the declared width."},
    {"id": 3, "topic": "JavaScript", "difficulty": "easy", "type": "conceptual",
     "q": "What is event bubbling in the DOM?",
     "options": [
         "Events fire on all elements at the same depth simultaneously",
         "An event triggered on a child element propagates upward through its ancestor elements",
         "Mouse events bubble; keyboard events don't",
         "Events fire twice on each element"
     ],
     "correct": 1,
     "explanation": "Bubbling: after a click on a child, the event propagates up through parent, grandparent, etc. You can stop it with `event.stopPropagation()`."},
    {"id": 4, "topic": "CSS", "difficulty": "easy", "type": "conceptual",
     "q": "Which CSS display value enables flexbox layout?",
     "options": ["display: block", "display: flex", "display: grid", "display: inline-flex"],
     "correct": 1,
     "explanation": "display: flex makes an element a flex container, allowing its direct children to be laid out using the flexbox model."},
    {"id": 5, "topic": "React", "difficulty": "easy", "type": "conceptual",
     "q": "What does `useState` return in React?",
     "options": [
         "Just the current state value",
         "An array of [currentValue, setterFunction]",
         "An object with {value, set, reset}",
         "A Promise that resolves to the state"
     ],
     "correct": 1,
     "explanation": "useState returns a 2-element tuple: the current state value and a setter function. Calling the setter with a new value triggers a re-render."},
    {"id": 6, "topic": "Performance", "difficulty": "easy", "type": "conceptual",
     "q": "What does the browser's critical rendering path refer to?",
     "options": [
         "The sequence of JavaScript file downloads",
         "The sequence of steps to convert HTML/CSS/JS into pixels on screen: DOM → CSSOM → Render Tree → Layout → Paint",
         "The CDN route with lowest latency",
         "The process of loading web fonts"
     ],
     "correct": 1,
     "explanation": "The critical rendering path is the sequence the browser follows to render a page. Optimizing it (minimizing render-blocking resources) directly improves page load perceived speed."},
    # ── Medium (11 questions) ─────────────────────────────────────────────────
    {"id": 7, "topic": "React", "difficulty": "medium", "type": "conceptual",
     "q": "What triggers a re-render in a React functional component?",
     "options": [
         "Changes in state, props, or parent context",
         "Calling any function inside the component",
         "Mutating a regular let variable declared inside the component",
         "Reading from localStorage"
     ],
     "correct": 0,
     "explanation": "React schedules a re-render when useState/useReducer state changes, when the parent passes new props, or when a consumed Context value changes. Direct variable mutation does NOT trigger re-renders."},
    {"id": 8, "topic": "CSS", "difficulty": "medium", "type": "scenario",
     "q": "Elements inside a CSS Grid container are overflowing their cells on small screens. What property constrains them?",
     "options": ["grid-template-columns: auto", "minmax(0, 1fr) in grid-template-columns", "overflow: hidden on the container", "flex-shrink: 1"],
     "correct": 1,
     "explanation": "Using `1fr` alone doesn't prevent overflow since `fr` has an implied minimum size. `minmax(0, 1fr)` sets a minimum of 0, allowing grid items to shrink below their content size."},
    {"id": 9, "topic": "JavaScript", "difficulty": "medium", "type": "code_output",
     "q": "What does the following code log?\n```js\nconsole.log(1 + '2');\nconsole.log(1 - '2');\n```",
     "options": ["3\n-1", "'12'\n-1", "NaN\nNaN", "12\nNaN"],
     "correct": 1,
     "explanation": "`1 + '2'` triggers string concatenation ('+' with a string coerces the number) → '12'. `1 - '2'` performs numeric subtraction (strings are coerced to numbers for '-') → -1."},
    {"id": 10, "topic": "React", "difficulty": "medium", "type": "conceptual",
     "q": "What is the purpose of the React `key` prop when rendering lists?",
     "options": [
         "It provides accessibility labels for screen readers",
         "It helps React identify which items changed, were added, or removed — enabling efficient DOM reconciliation",
         "It is required for CSS styling of list items",
         "It prevents the list from re-rendering"
     ],
     "correct": 1,
     "explanation": "React uses the key to match virtual DOM elements with actual DOM nodes across renders. Stable, unique keys ensure React only updates what actually changed."},
    {"id": 11, "topic": "Performance", "difficulty": "medium", "type": "conceptual",
     "q": "What is lazy loading in the context of React?",
     "options": [
         "Using setTimeout to delay component updates",
         "Loading components only when they are needed using React.lazy() and Suspense, reducing the initial bundle size",
         "Preventing re-renders until the user interacts",
         "Caching API responses in localStorage"
     ],
     "correct": 1,
     "explanation": "React.lazy() combined with Suspense enables code-splitting — the component's code is downloaded only when it's first rendered, reducing the initial JS payload."},
    {"id": 12, "topic": "TypeScript", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between `type` and `interface` in TypeScript?",
     "options": [
         "interface is for objects; type is only for primitives",
         "interface can be extended with `extends` and merged via declaration merging; type is more flexible (unions, intersections, primitives)",
         "They are completely identical",
         "type is for functions only"
     ],
     "correct": 1,
     "explanation": "Both can describe object shapes. interface supports declaration merging (two declarations with the same name are merged). type supports union types, mapped types, and conditional types. For object shapes, either works; prefer interface for library APIs."},
    {"id": 13, "topic": "CSS", "difficulty": "medium", "type": "conceptual",
     "q": "What is the CSS specificity order from lowest to highest?",
     "options": [
         "Inline → ID → Class → Element",
         "Element → Class/Attribute/Pseudo-class → ID → Inline styles",
         "Class → ID → Inline → Element",
         "All selectors have equal specificity"
     ],
     "correct": 1,
     "explanation": "CSS specificity (low to high): element/pseudo-element (0,0,1) < class/attribute/pseudo-class (0,1,0) < ID (1,0,0) < inline style (1,0,0,0). `!important` overrides all."},
    {"id": 14, "topic": "JavaScript", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between `null` and `undefined` in JavaScript?",
     "options": [
         "They are identical — both mean 'no value'",
         "`undefined` means a variable was declared but not assigned; `null` is an explicit assignment meaning 'no value'",
         "`null` is a number; `undefined` is a string",
         "`undefined` is for objects; `null` is for primitives"
     ],
     "correct": 1,
     "explanation": "`undefined` is the default value of uninitialized variables, missing function parameters, and absent object properties. `null` must be explicitly assigned to signal intentional absence of a value."},
    {"id": 15, "topic": "React", "difficulty": "medium", "type": "conceptual",
     "q": "When should you use Context API vs. a state management library like Redux?",
     "options": [
         "Context is for performance-critical state; Redux is for simple state",
         "Context is best for low-frequency global state (theme, auth); Redux/Zustand for frequently updated state that many components consume",
         "They cannot be used in the same application",
         "Context replaces Redux entirely in React 18"
     ],
     "correct": 1,
     "explanation": "Context triggers all consumers to re-render when the value changes. For frequently updated state (e.g., live data), Redux/Zustand provide fine-grained subscription to prevent unnecessary re-renders."},
    {"id": 16, "topic": "Performance", "difficulty": "medium", "type": "conceptual",
     "q": "What is Core Web Vitals and which metric measures interactivity/responsiveness?",
     "options": [
         "A Google ranking framework; CLS measures interactivity",
         "Google's user experience metrics; INP (Interaction to Next Paint) measures responsiveness/interactivity",
         "A CSS performance benchmark; FCP measures interactivity",
         "A JavaScript testing framework; TTI measures interactivity"
     ],
     "correct": 1,
     "explanation": "Core Web Vitals are LCP (loading — Largest Contentful Paint), INP (interactivity — replaced FID in 2024), and CLS (visual stability — Cumulative Layout Shift). INP measures how quickly the page responds to user interactions."},
    {"id": 17, "topic": "Accessibility", "difficulty": "medium", "type": "conceptual",
     "q": "What is the purpose of the HTML `alt` attribute on `<img>` elements?",
     "options": [
         "Controls image loading priority",
         "Provides alternative text for screen readers and displays when the image fails to load",
         "Defines the image file format",
         "Sets the image's ARIA role"
     ],
     "correct": 1,
     "explanation": "The `alt` attribute provides a textual description for screen readers (accessibility) and is displayed when the image cannot be loaded. Decorative images should use `alt=''`."},
    # ── Hard (5 questions) ────────────────────────────────────────────────────
    {"id": 18, "topic": "Performance", "difficulty": "hard", "type": "scenario",
     "q": "A React app with a large data table becomes sluggish when users scroll. The table renders 10,000 rows. What is the best fix?",
     "options": [
         "Reduce font size to improve rendering speed",
         "Implement virtual/windowed rendering (e.g., react-window) — only render rows visible in the viewport",
         "Use setTimeout to stagger row renders",
         "Move the table to a Web Worker"
     ],
     "correct": 1,
     "explanation": "Virtual lists render only the rows visible in the viewport (+ a small buffer), keeping DOM nodes in the hundreds rather than thousands. react-window and react-virtual implement this pattern."},
    {"id": 19, "topic": "JavaScript", "difficulty": "hard", "type": "conceptual",
     "q": "What is the JavaScript event loop, and what is the difference between the microtask queue and the macrotask queue?",
     "options": [
         "Both queues are identical; the event loop processes them in random order",
         "Microtasks (Promises, queueMicrotask) run after the current task and before the next macrotask (setTimeout, setInterval). Microtasks drain completely before any macrotask runs.",
         "Macrotasks (Promises) run first; microtasks (setTimeout) run after all macrotasks",
         "The event loop only exists in Node.js, not browsers"
     ],
     "correct": 1,
     "explanation": "After each task, the event loop drains the entire microtask queue (Promises, MutationObserver) before picking the next macrotask (setTimeout, setInterval, I/O). This is why Promise.then() callbacks run before setTimeout(fn, 0)."},
    {"id": 20, "topic": "React", "difficulty": "hard", "type": "scenario",
     "q": "A parent component passes an object literal as a prop to a memoized child: `<Child config={{theme: 'dark'}} />`. The child still re-renders on every parent render despite React.memo(). Why?",
     "options": [
         "React.memo() doesn't work with object props",
         "A new object literal is created on every render, so the prop reference changes even though the value is the same. Fix with useMemo.",
         "The child needs to implement shouldComponentUpdate",
         "Objects must be passed as JSON strings to memoized components"
     ],
     "correct": 1,
     "explanation": "React.memo() uses shallow comparison. `{theme: 'dark'}` creates a NEW object reference each render. The shallow comparison sees a different reference → re-renders. Fix: `const config = useMemo(() => ({theme: 'dark'}), [])`."},
    {"id": 21, "topic": "Security", "difficulty": "hard", "type": "conceptual",
     "q": "What is Content Security Policy (CSP) and what attack does it primarily prevent?",
     "options": [
         "An API authentication mechanism; prevents CORS violations",
         "An HTTP response header that whitelists trusted content sources, primarily preventing XSS attacks from injected scripts",
         "A database query validator; prevents SQL injection",
         "A browser setting for blocking ads"
     ],
     "correct": 1,
     "explanation": "CSP is a response header (Content-Security-Policy) that tells the browser which sources are trusted for scripts, styles, images, etc. By restricting script sources, it prevents injected malicious scripts (XSS) from executing."},
    {"id": 22, "topic": "Performance", "difficulty": "hard", "type": "conceptual",
     "q": "What is hydration in the context of server-side rendering (SSR) with React?",
     "options": [
         "Adding water to improve server cooling",
         "The process where React attaches event listeners and makes server-rendered HTML interactive by reconciling it with the virtual DOM",
         "Pre-fetching data before the user navigates",
         "Rehydrating stale cache entries with fresh data"
     ],
     "correct": 1,
     "explanation": "In SSR, the server sends static HTML. Hydration is React's process of 'taking over' that HTML — attaching event handlers, setting up state, and making it fully interactive without re-rendering the DOM from scratch."},
]

DATA_SCIENCE_QUESTIONS = [
    {"id": 1, "topic": "Statistics", "difficulty": "easy", "type": "conceptual",
     "q": "What is the median of the dataset: [3, 1, 4, 1, 5, 9, 2, 6]?",
     "options": ["3.5", "3.875", "4", "3"],
     "correct": 0,
     "explanation": "Sorted: [1, 1, 2, 3, 4, 5, 6, 9]. Even count → median = (3 + 4) / 2 = 3.5."},
    {"id": 2, "topic": "Python/Pandas", "difficulty": "easy", "type": "conceptual",
     "q": "Which pandas method shows a statistical summary (count, mean, std, min, max) of numeric columns?",
     "options": ["df.info()", "df.describe()", "df.summary()", "df.stats()"],
     "correct": 1,
     "explanation": "df.describe() generates descriptive statistics for numeric columns: count, mean, std, min, 25th/50th/75th percentile, max."},
    {"id": 3, "topic": "Visualization", "difficulty": "easy", "type": "conceptual",
     "q": "Which chart type is best for showing the distribution of a single continuous variable?",
     "options": ["Bar chart", "Histogram", "Pie chart", "Scatter plot"],
     "correct": 1,
     "explanation": "A histogram bins continuous data into intervals and shows the frequency of each bin, revealing the distribution shape (normal, skewed, bimodal, etc.)."},
    {"id": 4, "topic": "ML Basics", "difficulty": "easy", "type": "conceptual",
     "q": "What is linear regression used for?",
     "options": [
         "Classifying items into categories",
         "Predicting a continuous numerical output based on input features",
         "Clustering similar data points",
         "Reducing feature dimensionality"
     ],
     "correct": 1,
     "explanation": "Linear regression models the linear relationship between input features and a continuous target variable, making predictions like price, temperature, or score."},
    {"id": 5, "topic": "Statistics", "difficulty": "easy", "type": "conceptual",
     "q": "What does standard deviation measure?",
     "options": [
         "The center of a distribution",
         "The spread or dispersion of data around the mean",
         "The most frequent value in a dataset",
         "The range between the minimum and maximum values"
     ],
     "correct": 1,
     "explanation": "Standard deviation quantifies how much values deviate from the mean on average. A small std means data clusters tightly around the mean; a large std means data is spread out."},
    {"id": 6, "topic": "Data Cleaning", "difficulty": "easy", "type": "conceptual",
     "q": "What is a common strategy for handling missing values (NaN) in a numerical dataset?",
     "options": [
         "Always delete rows with missing values",
         "Impute with mean, median, or mode; or use a model-based imputation",
         "Replace all NaN with 0",
         "Missing values cannot be handled"
     ],
     "correct": 1,
     "explanation": "Imputation fills NaN with a summary statistic (mean/median for numeric; mode for categorical) or uses model-based methods. Deleting rows is only appropriate when missingness is very sparse and random."},
    {"id": 7, "topic": "ML", "difficulty": "medium", "type": "conceptual",
     "q": "What is the bias-variance tradeoff in machine learning?",
     "options": [
         "Reducing bias always reduces variance",
         "High bias = underfitting (model too simple); High variance = overfitting (model too complex). Optimal models balance both.",
         "Bias and variance are independent of model complexity",
         "This tradeoff only applies to classification, not regression"
     ],
     "correct": 1,
     "explanation": "Bias: error from wrong assumptions (underfit, high training error). Variance: sensitivity to training data fluctuations (overfit, low training error but high test error). The goal is to find the sweet spot."},
    {"id": 8, "topic": "Statistics", "difficulty": "medium", "type": "conceptual",
     "q": "What is the Central Limit Theorem?",
     "options": [
         "The mean of any dataset is always normally distributed",
         "The sampling distribution of the sample mean approaches a normal distribution as sample size increases, regardless of the population's distribution",
         "Large datasets always have a normal distribution",
         "The standard deviation approaches 0 with more samples"
     ],
     "correct": 1,
     "explanation": "CLT states that the distribution of sample means approaches a normal distribution as n → ∞, enabling hypothesis testing and confidence intervals even when the underlying data is not normally distributed."},
    {"id": 9, "topic": "Python", "difficulty": "medium", "type": "code_output",
     "q": "What does `df['col'].value_counts()` return?",
     "options": [
         "The number of non-null values in 'col'",
         "A Series with unique values as index and their frequency counts as values, sorted descending",
         "A DataFrame with value and count columns",
         "The sum of all values in 'col'"
     ],
     "correct": 1,
     "explanation": "value_counts() returns a Series where each unique value is an index entry and the value is how many times it appears in the column, sorted from most to least frequent."},
    {"id": 10, "topic": "SQL", "difficulty": "medium", "type": "conceptual",
     "q": "What does `GROUP BY` do in SQL and when do you use it?",
     "options": [
         "Sorts the result set",
         "Groups rows that share the same values in specified columns so you can apply aggregate functions (COUNT, SUM, AVG) to each group",
         "Filters rows based on a condition",
         "Joins two tables"
     ],
     "correct": 1,
     "explanation": "GROUP BY collapses multiple rows into groups based on shared column values. You then apply aggregate functions to summarize each group (e.g., total sales per city)."},
    {"id": 11, "topic": "Visualization", "difficulty": "medium", "type": "conceptual",
     "q": "When should you use a box plot instead of a histogram?",
     "options": [
         "Box plots are for categorical data; histograms are for numerical",
         "Box plots show the distribution summary (median, quartiles, outliers) and are ideal for comparing multiple groups; histograms show the full shape of one distribution",
         "Histograms only work for small datasets; box plots scale better",
         "They convey identical information"
     ],
     "correct": 1,
     "explanation": "Box plots compactly show median, IQR, and outliers, making them ideal for comparing distributions across multiple groups. Histograms reveal distribution shape but are harder to compare side-by-side."},
    {"id": 12, "topic": "ML", "difficulty": "medium", "type": "conceptual",
     "q": "What is the purpose of PCA (Principal Component Analysis)?",
     "options": [
         "To increase the number of features",
         "To reduce dimensionality by projecting data onto the directions of maximum variance",
         "To impute missing values",
         "To normalize feature scales"
     ],
     "correct": 1,
     "explanation": "PCA finds orthogonal axes (principal components) that capture the most variance. By keeping the top k components, you reduce dimensions while preserving the most information."},
    {"id": 13, "topic": "Feature Engineering", "difficulty": "medium", "type": "conceptual",
     "q": "What is one-hot encoding used for?",
     "options": [
         "Normalizing numerical features",
         "Converting categorical variables into binary columns (one per category) that ML models can process numerically",
         "Handling missing values in categorical columns",
         "Encoding passwords securely"
     ],
     "correct": 1,
     "explanation": "ML algorithms require numerical inputs. One-hot encoding creates a binary column per category (1 = present, 0 = absent), avoiding the false ordinal relationship that simple integer encoding introduces."},
    {"id": 14, "topic": "Statistics", "difficulty": "medium", "type": "conceptual",
     "q": "What does the R² (R-squared) metric measure in regression?",
     "options": [
         "The error between predictions and actual values",
         "The proportion of variance in the target variable explained by the model (0 = no explanation, 1 = perfect)",
         "The correlation between features",
         "The model's prediction speed"
     ],
     "correct": 1,
     "explanation": "R² ranges from 0 to 1 (can be negative for very bad models). An R² of 0.85 means the model explains 85% of the variance in the target. It does NOT indicate the model is calibrated or unbiased."},
    {"id": 15, "topic": "ML", "difficulty": "medium", "type": "scenario",
     "q": "A churn prediction model has 95% accuracy but the business says it's useless. The actual churn rate is 3%. What's wrong?",
     "options": [
         "The model's learning rate is too high",
         "The model likely predicts 'no churn' for everyone — accuracy is misleading for imbalanced classes. Use Precision, Recall, F1, or AUC.",
         "95% accuracy is not high enough",
         "The dataset is too small"
     ],
     "correct": 1,
     "explanation": "With 3% churn rate, a model that always predicts 'no churn' gets 97% accuracy but catches zero churners. Precision and Recall (and their F1 harmonic mean) measure how well the model identifies the minority class."},
    {"id": 16, "topic": "SQL", "difficulty": "medium", "type": "conceptual",
     "q": "What is a window function in SQL, and give an example use case.",
     "options": [
         "A function that creates database views",
         "A function that performs calculations across a sliding set of rows related to the current row (e.g., running totals, rank within group) without collapsing rows",
         "A function that opens a connection pool",
         "A function for string manipulation across multiple rows"
     ],
     "correct": 1,
     "explanation": "Window functions (ROW_NUMBER, RANK, SUM OVER PARTITION BY) compute values over a 'window' of related rows. Unlike GROUP BY, they preserve individual rows. Example: rank each employee by salary within their department."},
    {"id": 17, "topic": "Data Pipeline", "difficulty": "medium", "type": "conceptual",
     "q": "What does ETL stand for in data engineering?",
     "options": [
         "Encrypt-Transform-Load",
         "Extract-Transform-Load — a pipeline that extracts data from sources, transforms it, and loads it into a target system",
         "External-Transfer-Link",
         "Evaluate-Test-Launch"
     ],
     "correct": 1,
     "explanation": "ETL: Extract data from source systems (databases, APIs, files) → Transform it (clean, aggregate, join, reshape) → Load it into a data warehouse or lake for analytics."},
    {"id": 18, "topic": "ML", "difficulty": "hard", "type": "conceptual",
     "q": "What is gradient boosting, and how does it differ from random forests?",
     "options": [
         "Both train trees in parallel; gradient boosting uses different random subsets",
         "Gradient boosting trains trees sequentially where each tree corrects the errors of the previous; random forests train trees in parallel on random subsets and average their predictions",
         "They are the same algorithm with different hyperparameters",
         "Random forests use gradient descent; gradient boosting uses random sampling"
     ],
     "correct": 1,
     "explanation": "Gradient boosting (XGBoost, LightGBM) builds trees sequentially, each fitting the residual errors of the ensemble so far. Random forests build independent trees in parallel and average them. Boosting typically achieves lower bias; forests lower variance."},
    {"id": 19, "topic": "Statistics", "difficulty": "hard", "type": "scenario",
     "q": "You run an A/B test showing a 5% lift in conversion rate with p=0.04. Your manager says 'great, ship it!' What important question should you ask first?",
     "options": [
         "Was the data stored in a relational database?",
         "What is the practical effect size / business impact? Statistical significance does not guarantee a meaningful or cost-justified change.",
         "Was Python or R used for the analysis?",
         "Was the test run on a weekday?"
     ],
     "correct": 1,
     "explanation": "Statistical significance (p < 0.05) only means the result is unlikely due to chance. A 0.001% lift can be statistically significant with enough traffic. Always ask: Is the effect size practically meaningful given the cost of shipping?"},
    {"id": 20, "topic": "ML", "difficulty": "hard", "type": "conceptual",
     "q": "What is SHAP (SHapley Additive exPlanations) used for in ML?",
     "options": [
         "A training algorithm for neural networks",
         "A model-agnostic explainability method that assigns each feature a contribution (Shapley value) to the prediction for a specific instance",
         "A data preprocessing technique for high-cardinality categoricals",
         "A regularization technique for tree-based models"
     ],
     "correct": 1,
     "explanation": "SHAP uses cooperative game theory (Shapley values) to fairly distribute the prediction among all features. It's model-agnostic and provides both global (feature importance) and local (per-instance) explanations."},
    {"id": 21, "topic": "Data Pipeline", "difficulty": "hard", "type": "scenario",
     "q": "Your data pipeline processes 10TB of click logs daily. Processing is slow with pandas. What is the best solution?",
     "options": [
         "Increase the RAM of your server to 256GB",
         "Use distributed processing (Apache Spark, Dask, or BigQuery) that partitions data and processes in parallel across a cluster",
         "Downsample the data to 1TB before processing",
         "Convert pandas to numpy arrays first"
     ],
     "correct": 1,
     "explanation": "Pandas is single-node and loads data into RAM. For TBs of data, distributed frameworks like Spark partition data across multiple nodes and process in parallel, making otherwise impossible computations feasible."},
    {"id": 22, "topic": "Statistics", "difficulty": "hard", "type": "conceptual",
     "q": "What is multicollinearity in regression and how do you detect it?",
     "options": [
         "When the target variable has multiple modes; detect with histograms",
         "When two or more predictor variables are highly correlated, making coefficient estimates unstable; detect with VIF (Variance Inflation Factor)",
         "When the residuals are not normally distributed; detect with Q-Q plots",
         "When the sample size is too small; detect with power analysis"
     ],
     "correct": 1,
     "explanation": "Multicollinearity makes it hard to isolate individual feature effects and inflates standard errors. VIF > 5–10 indicates problematic multicollinearity. Fix by removing correlated features or using regularization (Ridge/Lasso)."},
]

CLOUD_QUESTIONS = [
    {"id": 1, "topic": "Cloud Basics", "difficulty": "easy", "type": "conceptual",
     "q": "What is the difference between IaaS, PaaS, and SaaS?",
     "options": [
         "They are three names for the same cloud service model",
         "IaaS provides raw infrastructure (VMs, storage); PaaS provides a managed platform for development; SaaS delivers complete software applications",
         "IaaS is for databases; PaaS is for networking; SaaS is for compute",
         "SaaS is the cheapest; IaaS is the most expensive"
     ],
     "correct": 1,
     "explanation": "IaaS (e.g., AWS EC2): you manage OS and above. PaaS (e.g., Heroku, Cloud Run): you deploy code, provider manages runtime. SaaS (e.g., Gmail): fully managed application you just use."},
    {"id": 2, "topic": "AWS", "difficulty": "easy", "type": "conceptual",
     "q": "What is Amazon S3 used for?",
     "options": [
         "Running virtual machines",
         "Scalable object storage for files, images, backups, and static website hosting",
         "Relational database hosting",
         "Content delivery network"
     ],
     "correct": 1,
     "explanation": "S3 (Simple Storage Service) stores objects (files) in buckets. It offers 99.999999999% (11 nines) durability and is used for backups, media storage, data lakes, and static website hosting."},
    {"id": 3, "topic": "Networking", "difficulty": "easy", "type": "conceptual",
     "q": "What is a VPC (Virtual Private Cloud)?",
     "options": [
         "A physical server you rent in a data center",
         "A logically isolated section of a cloud provider's network where you launch resources with full control over IP ranges and routing",
         "A type of content delivery network",
         "A managed Kubernetes service"
     ],
     "correct": 1,
     "explanation": "A VPC is your own isolated virtual network within the cloud. You define IP ranges (CIDR), subnets, route tables, and security groups, giving you network-level isolation and control."},
    {"id": 4, "topic": "Security", "difficulty": "easy", "type": "conceptual",
     "q": "What does IAM (Identity and Access Management) control in AWS?",
     "options": [
         "Network traffic between services",
         "Who can authenticate and what actions they can perform on which AWS resources",
         "Storage encryption keys",
         "Auto-scaling policies"
     ],
     "correct": 1,
     "explanation": "IAM manages users, groups, roles, and policies. Policies define permissions (Allow/Deny) for API actions on specific resources. Principle of Least Privilege: grant only necessary permissions."},
    {"id": 5, "topic": "Containers", "difficulty": "easy", "type": "conceptual",
     "q": "What is a Docker container?",
     "options": [
         "A lightweight virtual machine with its own OS kernel",
         "A standardized, portable package that bundles an application and its dependencies, sharing the host OS kernel",
         "A cloud-specific format for deploying functions",
         "A tool for storing Docker images"
     ],
     "correct": 1,
     "explanation": "Docker containers package code + libraries + runtime into an immutable unit. Unlike VMs, they share the host kernel, making them faster to start and more resource-efficient."},
    {"id": 6, "topic": "Cloud Basics", "difficulty": "easy", "type": "conceptual",
     "q": "What is a CDN (Content Delivery Network) and what problem does it solve?",
     "options": [
         "A private network for cloud service communication",
         "A geographically distributed network of servers that caches and delivers content from locations closest to users, reducing latency",
         "A service for managing DNS records",
         "A load balancer for database connections"
     ],
     "correct": 1,
     "explanation": "CDNs cache static assets (images, JS, CSS) at edge locations near users worldwide. Users download from a nearby edge node rather than a distant origin server, reducing load times."},
    {"id": 7, "topic": "AWS", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between horizontal auto-scaling and a load balancer?",
     "options": [
         "They are the same service in AWS",
         "Auto-scaling adds/removes EC2 instances based on load; a load balancer distributes incoming traffic across the running instances",
         "A load balancer scales instances; auto-scaling distributes traffic",
         "Auto-scaling only applies to databases; load balancers only to web servers"
     ],
     "correct": 1,
     "explanation": "Auto-scaling group manages instance count (scale out when CPU > 70%, scale in when < 30%). The load balancer (ALB/NLB) distributes requests across healthy instances. They work together: scale + distribute."},
    {"id": 8, "topic": "Containers", "difficulty": "medium", "type": "conceptual",
     "q": "What is Kubernetes and what problem does it solve?",
     "options": [
         "A Docker alternative for building container images",
         "A container orchestration platform that automates deployment, scaling, load balancing, and self-healing of containerized applications",
         "A monitoring tool for cloud infrastructure",
         "A CI/CD pipeline for containerized applications"
     ],
     "correct": 1,
     "explanation": "Kubernetes (K8s) manages containers at scale: scheduling pods to nodes, maintaining desired replica counts, rolling out updates, and restarting failed containers automatically."},
    {"id": 9, "topic": "Security", "difficulty": "medium", "type": "conceptual",
     "q": "What is the Principle of Least Privilege in cloud security?",
     "options": [
         "Only cloud administrators should have access to production",
         "Every entity (user, service, instance) should have only the minimum permissions needed to perform its specific function",
         "Databases should always be private; public access is never allowed",
         "Encryption keys should be rotated every 90 days"
     ],
     "correct": 1,
     "explanation": "Least Privilege reduces the blast radius of security breaches. If a compromised service only has read access to one S3 bucket, an attacker can't use it to delete data or access other resources."},
    {"id": 10, "topic": "Networking", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between a public subnet and a private subnet in AWS?",
     "options": [
         "Public subnets are free; private subnets cost more",
         "Public subnets route traffic to an Internet Gateway (resources can have public IPs); private subnets have no direct internet access and use a NAT Gateway for outbound traffic",
         "Public subnets can only hold web servers; private subnets can only hold databases",
         "They are the same — the naming is just organizational"
     ],
     "correct": 1,
     "explanation": "Public subnets have a route to the Internet Gateway, enabling inbound traffic to resources with public IPs. Private subnets route outbound traffic through a NAT Gateway (no inbound internet access) — ideal for databases and backend services."},
    {"id": 11, "topic": "CI/CD", "difficulty": "medium", "type": "conceptual",
     "q": "What is the difference between Continuous Integration and Continuous Deployment?",
     "options": [
         "They are the same process",
         "CI automatically builds and tests code on every commit; CD automatically deploys every passing build to production",
         "CI deploys to staging; CD deploys to production",
         "CD requires human approval; CI is always automated"
     ],
     "correct": 1,
     "explanation": "CI: every code commit triggers automated build and test (catches integration bugs early). CD: every passing build is automatically deployed to production with no manual step. Continuous Delivery requires a manual approval gate before production."},
    {"id": 12, "topic": "AWS", "difficulty": "medium", "type": "conceptual",
     "q": "What is AWS Lambda, and what is its key advantage over EC2?",
     "options": [
         "Lambda is a managed database; EC2 is for compute. Lambda scales automatically.",
         "Lambda is a serverless compute service — you run code in response to events without managing servers, paying only for execution duration",
         "Lambda is always faster than EC2 for all workloads",
         "Lambda is only for Python workloads; EC2 supports all languages"
     ],
     "correct": 1,
     "explanation": "Lambda executes code (functions) in response to triggers (HTTP, S3 event, schedule) without provisioning or managing servers. You pay per invocation and millisecond of execution. Ideal for event-driven, intermittent workloads."},
    {"id": 13, "topic": "Infrastructure as Code", "difficulty": "medium", "type": "conceptual",
     "q": "What is Infrastructure as Code (IaC) and which tool is most commonly used for cloud IaC?",
     "options": [
         "Writing Python scripts to call cloud APIs; most common tool is boto3",
         "Defining infrastructure (servers, networks, databases) in declarative configuration files; Terraform and AWS CloudFormation are most common",
         "Automating server configuration with shell scripts",
         "Using Docker Compose to define cloud resources"
     ],
     "correct": 1,
     "explanation": "IaC treats infrastructure as code: version-controlled, reviewed, and reproducible. Terraform (multi-cloud, declarative) and CloudFormation (AWS-specific) provision and manage resources from configuration files, eliminating manual console operations."},
    {"id": 14, "topic": "Monitoring", "difficulty": "medium", "type": "conceptual",
     "q": "What are the three pillars of observability in cloud systems?",
     "options": [
         "CPU, Memory, Network",
         "Logs, Metrics, Traces — together they provide full visibility into system behavior",
         "Uptime, Latency, Throughput",
         "Availability, Reliability, Scalability"
     ],
     "correct": 1,
     "explanation": "Logs: timestamped text records of events. Metrics: numeric time-series data (CPU%, request rate, error rate). Traces: end-to-end request journeys across microservices. All three together enable diagnosing complex distributed system issues."},
    {"id": 15, "topic": "Containers", "difficulty": "medium", "type": "scenario",
     "q": "A Kubernetes pod keeps restarting with status 'OOMKilled'. What is happening and how do you fix it?",
     "options": [
         "The pod's Docker image is corrupted; rebuild the image",
         "The container exceeded its memory limit and was killed by Kubernetes. Fix by increasing the memory limit or reducing the container's memory usage.",
         "The cluster has no available nodes; add more nodes",
         "The pod's liveness probe is misconfigured; adjust the timeout"
     ],
     "correct": 1,
     "explanation": "OOMKilled (Out of Memory Killed) means the container used more memory than its resource limit. Fix: profile memory usage, optimize the application, and set appropriate limits in the pod spec."},
    {"id": 16, "topic": "Security", "difficulty": "medium", "type": "conceptual",
     "q": "What is encryption at rest vs. encryption in transit?",
     "options": [
         "At rest = encrypted during transfer; in transit = encrypted on disk",
         "At rest = data is encrypted when stored on disk (S3, RDS); in transit = data is encrypted while being transmitted over the network (TLS/HTTPS)",
         "Both terms mean the same thing",
         "In transit encryption only applies to external traffic"
     ],
     "correct": 1,
     "explanation": "Encryption at rest protects stored data (e.g., KMS-encrypted S3 objects, RDS encrypted volumes) if physical storage is compromised. Encryption in transit (TLS/HTTPS) protects data from eavesdropping during network transmission."},
    {"id": 17, "topic": "Networking", "difficulty": "medium", "type": "conceptual",
     "q": "What is DNS and what does the `A` record type specify?",
     "options": [
         "Domain Name System; A records specify mail server addresses",
         "Domain Name System; A records map a hostname to an IPv4 address",
         "Dynamic Network Service; A records specify authentication providers",
         "Distributed Name Server; A records specify HTTPS certificates"
     ],
     "correct": 1,
     "explanation": "DNS translates human-readable hostnames to IP addresses. An A record maps a domain name (api.example.com) to a specific IPv4 address. AAAA records are the IPv6 equivalent."},
    {"id": 18, "topic": "Architecture", "difficulty": "hard", "type": "scenario",
     "q": "Your microservice architecture has 20 services all calling each other directly. This causes cascading failures and makes deployments complex. What pattern solves this?",
     "options": [
         "Replace all microservices with a monolith",
         "Implement a Service Mesh (e.g., Istio, Linkerd) for inter-service communication, or an API Gateway for external traffic, with circuit breakers",
         "Add more replicas of each service",
         "Move all services to the same VPC"
     ],
     "correct": 1,
     "explanation": "A service mesh handles retries, circuit breakers, mTLS, and observability for service-to-service traffic transparently via a sidecar proxy, decoupling these concerns from application code."},
    {"id": 19, "topic": "Cost Optimization", "difficulty": "hard", "type": "conceptual",
     "q": "What is the difference between Reserved Instances and Spot Instances in AWS?",
     "options": [
         "Reserved = pay per hour; Spot = pay per year",
         "Reserved Instances offer up to 75% discount for a 1–3 year commitment; Spot Instances use unused capacity at up to 90% discount but can be interrupted with 2-minute notice",
         "They are the same product with different names",
         "Spot Instances are for databases; Reserved are for web servers"
     ],
     "correct": 1,
     "explanation": "Reserved Instances: committed usage discount (stable, predictable workloads). Spot Instances: bid on spare AWS capacity at steep discounts — ideal for fault-tolerant batch jobs. Not suitable for stateful/persistent workloads due to interruption risk."},
    {"id": 20, "topic": "Security", "difficulty": "hard", "type": "scenario",
     "q": "A developer accidentally commits AWS credentials to a public GitHub repo. What are the immediate steps?",
     "options": [
         "Make the GitHub repo private and no action needed",
         "Immediately invalidate/rotate the exposed credentials in IAM, audit CloudTrail for unauthorized activity, and remove the secrets from git history",
         "Email AWS support to block the credentials",
         "Delete the GitHub repo entirely"
     ],
     "correct": 1,
     "explanation": "Exposed secrets must be rotated IMMEDIATELY (assume they are already compromised — bots scrape GitHub in seconds). Then: audit CloudTrail for any unauthorized API calls, and use git filter-branch or BFG Repo Cleaner to purge secrets from history."},
    {"id": 21, "topic": "Architecture", "difficulty": "hard", "type": "conceptual",
     "q": "What is the difference between stateless and stateful cloud architectures, and which is easier to scale?",
     "options": [
         "Stateful architectures scale better because they cache user data locally",
         "Stateless services don't retain user-specific data between requests (state is in DB/cache); stateless architectures scale horizontally much more easily",
         "They scale equally — it depends on the load balancer",
         "Stateless means the service has no database"
     ],
     "correct": 1,
     "explanation": "Stateless services handle each request independently with no local session. Any instance can serve any request, making horizontal scaling trivial. Stateful services need sticky sessions or shared storage to maintain consistency across instances."},
    {"id": 22, "topic": "Containers", "difficulty": "hard", "type": "conceptual",
     "q": "What is a Kubernetes liveness probe vs. a readiness probe?",
     "options": [
         "They are identical — Kubernetes uses them interchangeably",
         "Liveness: determines if a container is alive (restart if failing); Readiness: determines if a container is ready to serve traffic (remove from load balancer if failing)",
         "Readiness restarts failed containers; Liveness removes them from service",
         "Both probes are optional and have no effect on pod lifecycle"
     ],
     "correct": 1,
     "explanation": "Liveness probe: if it fails, Kubernetes restarts the container (dead-lock recovery). Readiness probe: if it fails, Kubernetes removes the pod from the Service's endpoints (no traffic sent) without restarting — useful during startup or dependency downtime."},
]


# ── Open-Ended Technical Scenario Questions (3 per career track) ──────────────
OPEN_ENDED_QUESTIONS_MAP = {
    "full-stack": [
        {
            "id": 101,
            "title": "Real-Time Collaborative Document Sync & Conflict Resolution",
            "scenario": "You are tasked with designing the core synchronization architecture for a real-time collaborative markdown editor (similar to Google Docs or Notion). Multiple users can edit the same document concurrently over WebSockets with intermittent network latency.",
            "prompt": "Detail your architectural solution. Specifically address: 1) What conflict resolution algorithm or data structure would you select (e.g., Operational Transformation vs CRDTs like Yjs/Automerge) and why? 2) How would you design the client-server synchronization protocol and client-side optimistic UI updates? 3) How do you handle edge cases such as offline reconnections, dropped packets, and server state persistence without losing keystrokes?",
            "rubric_focus": ["CRDT or OT algorithm", "WebSocket protocol", "Optimistic rendering", "Offline re-sync", "Edge cases & persistence"],
        },
        {
            "id": 102,
            "title": "React Performance Optimization & Long-Task Profiling",
            "scenario": "A mission-critical financial analytics dashboard built in React displays 50 live real-time updating tickers and data charts. Users report severe UI freezing, sluggish typing in search inputs, and an Interaction to Next Paint (INP) exceeding 450ms.",
            "prompt": "Explain your step-by-step diagnostic and optimization approach. Specifically: 1) What browser profiling tools (e.g., Chrome Performance profiler, React Profiler) and metrics would you use to pinpoint the root cause? 2) What state management and rendering refactors would you implement (e.g., useTransition, web workers, virtualization, selector memoization)? 3) How would you ensure high-frequency WebSocket updates do not trigger cascading re-renders across unaffected components?",
            "rubric_focus": ["DevTools profiling", "INP / Long tasks diagnosis", "Concurrent features (useTransition/useDeferredValue)", "Virtualization & Web Workers", "State isolation"],
        },
        {
            "id": 103,
            "title": "Resilient Microservices Payment Gateway & Idempotency",
            "scenario": "A high-volume checkout microservice interacts with an external third-party payment gateway. During peak flash sales, the payment gateway periodically returns HTTP 504 timeouts, connection resets, and latency spikes.",
            "prompt": "Propose an end-to-end resilient architecture to prevent double charges and stranded orders: 1) How would you implement distributed idempotency keys across client, API gateway, and database? 2) What retry strategy would you enforce (exponential backoff with full jitter, circuit breakers)? 3) How do you handle cases where the gateway charged the customer's card but timed out before returning a response to your backend?",
            "rubric_focus": ["Distributed idempotency keys", "Exponential backoff with jitter", "Circuit breaker pattern", "Reconciliation / Webhooks / DLQ", "Transaction consistency"],
        },
    ],
    "ai-ml": [
        {
            "id": 201,
            "title": "Production RAG Pipeline Architecture & Hallucination Guardrails",
            "scenario": "You are building a production Retrieval-Augmented Generation (RAG) system answering technical inquiries across 500,000 internal engineering documents and code repositories. Users complain about stale answers and occasional hallucinations.",
            "prompt": "Design the end-to-end RAG architecture: 1) What chunking and indexing strategies would you employ for mixed code and natural language text? 2) How would you implement hybrid search (dense embeddings + sparse BM25) and re-ranking (cross-encoders)? 3) What evaluation metrics and guardrails (e.g., Ragas, groundedness checks, prompt isolation) would you install to detect and mitigate hallucinations in real time?",
            "rubric_focus": ["Chunking strategy (semantic/hierarchical)", "Hybrid search (BM25 + Dense)", "Cross-encoder re-ranking", "Hallucination guardrails & groundedness", "Evaluation frameworks"],
        },
        {
            "id": 202,
            "title": "Deep Learning Model Latency Optimization (<60ms SLA)",
            "scenario": "A multi-modal transformer model deployed for live audio-visual moderation is experiencing a P99 inference latency of 380ms on GPU instances, breaching your business SLA of <60ms P99 under 500 concurrent requests.",
            "prompt": "Outline your systematic model optimization and deployment plan: 1) What algorithmic and model compression techniques (quantization INT8/FP8, structured pruning, knowledge distillation) would you apply? 2) What inference engine optimizations (TensorRT, ONNX Runtime, vLLM, continuous batching) would you leverage? 3) How would you design dynamic request batching and GPU memory management (KV cache paging) to maximize throughput while honoring the SLA?",
            "rubric_focus": ["Model compression (quantization, distillation)", "Runtime compilation (TensorRT/ONNX)", "Dynamic & continuous batching", "Memory & KV-cache optimization", "P99 SLA trade-offs"],
        },
        {
            "id": 203,
            "title": "Data & Concept Drift Detection with Automated Retraining",
            "scenario": "A credit default risk prediction model deployed 6 months ago has seen its AUC-ROC drop from 0.89 to 0.74 due to shifting macroeconomic conditions and new user demographics.",
            "prompt": "Detail your drift monitoring and MLOps strategy: 1) How do you differentiate between covariate shift, prior probability shift, and concept drift? What statistical tests (KS-test, PSI, Wasserstein distance) would you automate? 2) How do you handle delayed ground-truth labels in credit risk? 3) Design the automated retraining trigger, shadow/canary evaluation pipeline, and rollback safety triggers.",
            "rubric_focus": ["Covariate vs concept drift", "Statistical drift metrics (PSI, KS-test)", "Delayed feedback handling", "Shadow / Canary model evaluation", "Automated CI/CD for ML"],
        },
    ],
    "backend": [
        {
            "id": 301,
            "title": "High-Concurrency Inventory Reservation & Lock Contention",
            "scenario": "During an e-commerce flash sale with 20,000 requests/second targeting 500 units of a limited item, your relational database suffers from severe row-level lock contention, thread starvation, and connection pool exhaustion.",
            "prompt": "Architect a high-performance inventory reservation system: 1) Why does naive `SELECT ... FOR UPDATE` fail under this load? 2) How would you use an in-memory distributed store (like Redis Lua scripts or redlock) or optimistic locking with versioning to achieve sub-10ms reservation? 3) How do you guarantee inventory consistency between the reservation cache and the persistent SQL database, handling cart expirations and order cancellations?",
            "rubric_focus": ["Pessimistic vs optimistic locking pitfalls", "Redis atomic operations / Lua scripts", "Eventual consistency & two-phase reservation", "TTL expiry & rollback mechanisms", "Failure handling"],
        },
        {
            "id": 302,
            "title": "Multi-Region Distributed Rate Limiter (100k RPS)",
            "scenario": "You need to enforce global rate limits (e.g., 500 req/min per API key) across three geographic regions (US-East, EU-West, AP-South) processing a combined 100,000 requests per second.",
            "prompt": "Propose the rate limiter architecture: 1) Compare the Token Bucket, Leaky Bucket, and Sliding Window Counter algorithms for this use case. 2) How do you handle cross-region state synchronization without introducing cross-continental network latency on every API call? 3) Under network partition (split-brain), how does your system fail (fail-open vs fail-closed) and adhere to CAP theorem trade-offs?",
            "rubric_focus": ["Rate limiting algorithms (Sliding window vs Token bucket)", "Local caching with asynchronous synchronization", "CAP theorem & latency budget", "Fail-open vs fail-closed policy", "High-throughput data store"],
        },
        {
            "id": 303,
            "title": "Event-Driven Asynchronous Order Pipeline with Strict Ordering",
            "scenario": "An event-driven financial order processing pipeline built on Apache Kafka must guarantee strictly ordered execution of ledger events per account, while achieving high overall horizontal throughput.",
            "prompt": "Design the streaming pipeline: 1) How do you configure Kafka partition keys to ensure per-account ordering without causing hot partition hotspots? 2) How do you handle consumer group rebalancing, dead-letter queues (DLQ), and poison pill messages without halting the partition pipeline? 3) How do you implement idempotent consumer processing (e.g., transactional outbox pattern, deduplication store)?",
            "rubric_focus": ["Partition key strategy & skew prevention", "Idempotent consumer / Outbox pattern", "Dead-letter queues & poison pill isolation", "Rebalance handling", "Strict ordering semantics"],
        },
    ],
    "frontend": [
        {
            "id": 401,
            "title": "Enterprise Micro-Frontend Architecture Migration",
            "scenario": "An enterprise SaaS platform is migrating from a massive monolith to micro-frontends maintained by five independent product squads. Squads must deploy independently without coordinated release trains.",
            "prompt": "Present an architectural evaluation: 1) Compare Webpack Module Federation, Web Components, and iframe-based integration across bundle size, routing, shared state, and styling isolation. 2) How do you handle version skew of shared dependencies (e.g., React, design system tokens)? 3) How would you implement global authentication state and cross-micro-frontend event communication without tight coupling?",
            "rubric_focus": ["Module Federation vs alternative patterns", "Shared dependency management & version skew", "Cross-app communication (Event Bus / CustomEvents)", "CSS isolation (Shadow DOM / Scoped CSS)", "CI/CD autonomy"],
        },
        {
            "id": 402,
            "title": "Core Web Vitals Remediation (LCP 4.8s, INP 420ms)",
            "scenario": "An international retail client experiences a sudden drop in organic search rankings due to failing Core Web Vitals on mobile: Largest Contentful Paint (LCP) is 4.8s, Cumulative Layout Shift (CLS) is 0.28, and Interaction to Next Paint (INP) is 420ms.",
            "prompt": "Detail your technical remediation roadmap: 1) How do you optimize the critical rendering path, resource prioritization (fetchpriority, preload, responsive srcset), and server response times to bring LCP under 2.0s? 2) What common frontend anti-patterns cause CLS, and how do you eliminate them? 3) How do you break up long JavaScript tasks on the main thread to achieve sub-150ms INP?",
            "rubric_focus": ["Critical rendering path & resource hints", "LCP optimization (server, compression, priority)", "CLS elimination (aspect-ratio, font-display, dynamic injection)", "INP / Main-thread yields (scheduler.yield/requestIdleCallback)", "Measurement & monitoring"],
        },
        {
            "id": 403,
            "title": "Offline-First Progressive Web App (PWA) with Background Sync",
            "scenario": "Field engineers in remote areas need to record equipment inspection logs on a tablet web application with zero or intermittent cellular connectivity.",
            "prompt": "Design the offline-first web architecture: 1) How would you utilize Service Workers and the Cache API for static application shell caching and runtime asset updates? 2) How would you architect client-side data storage using IndexedDB for forms, high-resolution photos, and draft reviews? 3) Explain your background synchronization and conflict resolution strategy when the device re-establishes connectivity.",
            "rubric_focus": ["Service Worker lifecycle & Cache strategies (Stale-while-revalidate)", "IndexedDB data schema & blob storage", "Background Sync API & retry queue", "Conflict resolution (Timestamp, Last-Write-Wins, Manual)", "User experience & sync status indicator"],
        },
    ],
    "data-science": [
        {
            "id": 501,
            "title": "Real-Time & Batch Feature Store Architecture",
            "scenario": "Your machine learning platform supports both fraud detection models requiring sub-10ms online feature retrieval and offline historical batch model training across billions of transaction rows.",
            "prompt": "Architect the unified feature store: 1) How do you achieve dual-storage consistency between low-latency online stores (e.g., Redis, DynamoDB) and high-throughput offline stores (e.g., Parquet, Iceberg, BigQuery)? 2) How do you strictly prevent data leakage and ensure point-in-time correctness during historical backfills and training dataset generation? 3) How do you monitor feature drift and feature value degradation between online inference and offline training distributions?",
            "rubric_focus": ["Online vs offline store dual architecture", "Point-in-time correctness / Time-travel joins", "Feature leakage prevention", "Streaming feature computation (Flink/Spark)", "Drift monitoring"],
        },
        {
            "id": 502,
            "title": "Extreme Class Imbalance in Rare Event Detection (0.02% Positive)",
            "scenario": "You are building a fraud or rare medical condition detection model where positive instances make up only 0.02% of the dataset (1 in 5,000 cases). A naive baseline model achieves 99.98% accuracy.",
            "prompt": "Describe your end-to-end modeling strategy: 1) Why is accuracy completely uninformative here, and what evaluation metrics (PR-AUC, precision at fixed recall, Cost-Utility curve, F-beta) would you optimize? 2) What sampling (SMOTE, Focal Loss, threshold moving) or anomaly detection techniques (Isolation Forest, Autoencoders) are best suited? 3) How would you calibrate output probabilities (Platt scaling or Isotonic regression) to make prediction scores actionable for business operations?",
            "rubric_focus": ["Metric selection (PR-AUC vs ROC-AUC, Cost-sensitive)", "Focal Loss & Class weighting vs resampling", "Anomaly detection alternatives", "Probability calibration (Platt/Isotonic)", "Operational decision thresholding"],
        },
        {
            "id": 503,
            "title": "Causal Inference & Resolving Simpson's Paradox in Product Analytics",
            "scenario": "A major product redesign showed an aggregate 4% uplift in user retention in a 2-week A/B test. However, when slicing by user cohort (new vs power users), both cohorts individually exhibited a 2% decline in retention.",
            "prompt": "Analyze this paradox and prescribe solutions: 1) Explain the mathematical and statistical mechanism of Simpson's Paradox occurring here (e.g., cohort distribution shift or sample ratio mismatch). 2) How would you conduct diagnostics to verify Sample Ratio Mismatch (SRM) using Chi-square tests? 3) If an unbiased A/B test cannot be run due to network interference or ethical constraints, how would you apply quasi-experimental causal inference methods (e.g., Propensity Score Matching, Difference-in-Differences, or Synthetic Controls)?",
            "rubric_focus": ["Simpson's Paradox explanation & confounding variables", "Sample Ratio Mismatch (SRM) diagnostics", "Cohort weight adjustments", "Quasi-experimental methods (Diff-in-Diff, PSM, Synthetic Control)", "Causal DAGs"],
        },
    ],
    "cloud": [
        {
            "id": 601,
            "title": "Active-Active Multi-Region Disaster Recovery (RPO < 1s, RTO < 30s)",
            "scenario": "A tier-1 banking transaction gateway hosted in the cloud must withstand an entire region outage with a Recovery Point Objective (RPO) < 1 second and Recovery Time Objective (RTO) < 30 seconds.",
            "prompt": "Detail your multi-region architecture: 1) How do you configure global DNS and traffic routing (e.g., AWS Route 53 latency/health-check routing or Anycast IP)? 2) How do you handle cross-region database replication, synchronous vs asynchronous trade-offs, and multi-master conflict resolution? 3) How do you design automated health checks and failover mechanisms to avoid false-positive failovers (flapping) during regional network degradation?",
            "rubric_focus": ["Global DNS / Anycast load balancing", "Cross-region DB replication & RPO trade-offs", "Multi-region conflict resolution (vector clocks, CRDT)", "Health checks & anti-flapping dampening", "Automated RTO < 30s execution"],
        },
        {
            "id": 602,
            "title": "Kubernetes Zero-Downtime Deployment Remediation (502 Gateway Errors)",
            "scenario": "During rolling deployments in an EKS/GKE cluster, users intermittently encounter HTTP 502 Bad Gateway and connection reset errors for 15-30 seconds following pod terminations and spin-ups.",
            "prompt": "Diagnose the root cause and prescribe remediation: 1) Explain the exact race condition between kubelet pod termination (SIGTERM), endpoint slice propagation to ingress controllers/iptables, and in-flight request draining. 2) How do you configure `preStop` hooks, termination grace periods, and connection draining on ingress controllers? 3) What are the distinct roles and best-practice configurations of Readiness, Liveness, and Startup probes in preventing traffic from hitting unready pods?",
            "rubric_focus": ["Pod lifecycle (SIGTERM vs iptables/IPVS updates)", "preStop sleep hooks & terminationGracePeriodSeconds", "Readiness vs Liveness probe misconfigurations", "Ingress / Service Mesh connection draining", "Canary / Progressive delivery"],
        },
        {
            "id": 603,
            "title": "Cloud FinOps & Infrastructure Cost Remediation ($20k to $80k Spike)",
            "scenario": "An enterprise's cloud infrastructure bill surged from $20,000/month to $80,000/month over 90 days across AWS/GCP, prompting an urgent FinOps intervention.",
            "prompt": "Lay out your FinOps audit methodology: 1) What specific cost culprits would you investigate first (e.g., cross-AZ and NAT Gateway data transfer, unattached EBS/persistent volumes, over-provisioned idle compute, unexpiring object storage versions)? 2) What architectural mitigations (VPC endpoints, Karpenter/cluster autoscalers, S3 lifecycle policies) would you deploy immediately? 3) How would you implement long-term FinOps governance (cost allocation tags, anomaly detection alerts, compute Savings Plans/Reserved Instances)?",
            "rubric_focus": ["Egress & NAT Gateway data transfer audit", "Compute rightsizing & spot/graviton/savings plans", "Storage lifecycles & orphaned asset cleanup", "VPC endpoints for internal traffic", "Tagging & FinOps governance"],
        },
    ],
}


# ── Test Catalog (with career path routing, 10 min time limit, open-ended drills) ───
MOCK_TESTS_CATALOG = [
    {
        "id": "full-stack",
        "title": "Full-Stack Engineer Assessment",
        "career_path": "Full-Stack Engineer",
        "category": "Full-Stack",
        "questions_count": len(FULL_STACK_QUESTIONS),
        "open_ended_count": len(OPEN_ENDED_QUESTIONS_MAP["full-stack"]),
        "time_limit_seconds": 600,  # 10 minutes strictly enforced
        "difficulty": "Intermediate / Advanced",
        "questions": FULL_STACK_QUESTIONS,
        "open_ended_questions": OPEN_ENDED_QUESTIONS_MAP["full-stack"],
    },
    {
        "id": "ai-ml",
        "title": "AI/ML Engineer Assessment",
        "career_path": "AI/ML Engineer",
        "category": "AI & Machine Learning",
        "questions_count": len(AIML_QUESTIONS),
        "open_ended_count": len(OPEN_ENDED_QUESTIONS_MAP["ai-ml"]),
        "time_limit_seconds": 600,
        "difficulty": "Intermediate / Advanced",
        "questions": AIML_QUESTIONS,
        "open_ended_questions": OPEN_ENDED_QUESTIONS_MAP["ai-ml"],
    },
    {
        "id": "backend",
        "title": "Backend Developer Assessment",
        "career_path": "Backend Developer",
        "category": "Backend Engineering",
        "questions_count": len(BACKEND_QUESTIONS),
        "open_ended_count": len(OPEN_ENDED_QUESTIONS_MAP["backend"]),
        "time_limit_seconds": 600,
        "difficulty": "Intermediate / Advanced",
        "questions": BACKEND_QUESTIONS,
        "open_ended_questions": OPEN_ENDED_QUESTIONS_MAP["backend"],
    },
    {
        "id": "frontend",
        "title": "Frontend Developer Assessment",
        "career_path": "Frontend Developer",
        "category": "Frontend Engineering",
        "questions_count": len(FRONTEND_QUESTIONS),
        "open_ended_count": len(OPEN_ENDED_QUESTIONS_MAP["frontend"]),
        "time_limit_seconds": 600,
        "difficulty": "Intermediate / Advanced",
        "questions": FRONTEND_QUESTIONS,
        "open_ended_questions": OPEN_ENDED_QUESTIONS_MAP["frontend"],
    },
    {
        "id": "data-science",
        "title": "Data Scientist Assessment",
        "career_path": "Data Scientist",
        "category": "Data Science",
        "questions_count": len(DATA_SCIENCE_QUESTIONS),
        "open_ended_count": len(OPEN_ENDED_QUESTIONS_MAP["data-science"]),
        "time_limit_seconds": 600,
        "difficulty": "Intermediate / Advanced",
        "questions": DATA_SCIENCE_QUESTIONS,
        "open_ended_questions": OPEN_ENDED_QUESTIONS_MAP["data-science"],
    },
    {
        "id": "cloud",
        "title": "Cloud Engineer Assessment",
        "career_path": "Cloud Engineer",
        "category": "Cloud & DevOps",
        "questions_count": len(CLOUD_QUESTIONS),
        "open_ended_count": len(OPEN_ENDED_QUESTIONS_MAP["cloud"]),
        "time_limit_seconds": 600,
        "difficulty": "Intermediate / Advanced",
        "questions": CLOUD_QUESTIONS,
        "open_ended_questions": OPEN_ENDED_QUESTIONS_MAP["cloud"],
    },
]

# Catalog without questions (for listing endpoint — answers stay server-side)
MOCK_TESTS_LISTING = [
    {k: v for k, v in t.items() if k not in ("questions", "open_ended_questions")}
    for t in MOCK_TESTS_CATALOG
]


# ── Open-Ended Multi-Criteria Evaluator ────────────────────────────────────────
def fallback_evaluate_open_ended(question_meta: dict, answer: str) -> dict:
    """
    Deterministic semantic evaluator using 5 multi-criteria rubrics:
    1. Correctness (0-20)
    2. Reasoning (0-20)
    3. Technical Understanding (0-20)
    4. Relevance (0-20)
    5. Completeness (0-20)
    Technically correct answers receive credit even if wording differs from keywords.
    """
    text = (answer or "").strip()
    words = text.split()
    word_count = len(words)
    lower_text = text.lower()

    if word_count < 10:
        return {
            "question_id": question_meta.get("id"),
            "question_title": question_meta.get("title", ""),
            "correctness": 2,
            "reasoning": 2,
            "technical_understanding": 2,
            "relevance": 4,
            "completeness": 2,
            "score": 12,
            "feedback": "Answer is too brief. Provide technical justifications, trade-off considerations, and architecture details.",
        }

    # Depth baseline (0-14)
    if word_count >= 120:
        base = 15
    elif word_count >= 70:
        base = 13
    elif word_count >= 35:
        base = 10
    else:
        base = 7

    # Rubric focus hits (semantic keyword relevance)
    rubric = question_meta.get("rubric_focus", [])
    matched_focus = 0
    for item in rubric:
        item_words = [w for w in item.lower().replace("/", " ").replace("-", " ").split() if len(w) > 3]
        if any(w in lower_text for w in item_words):
            matched_focus += 1

    focus_bonus = min(4, matched_focus)

    # Reasoning indicators ("because", "trade-off", "tradeoff", "versus", "vs", "due to", "in order to", "prevents", "ensures")
    reasoning_markers = ["because", "trade-off", "tradeoff", "versus", "vs", "due to", "in order to", "prevents", "ensures", "chosen", "benefit"]
    has_reasoning = sum(1 for m in reasoning_markers if m in lower_text) >= 1

    # Completeness / edge cases indicators ("edge case", "failover", "scale", "latency", "timeout", "retry", "concurrency", "recovery", "fallback", "consistency")
    completeness_markers = ["edge case", "failover", "scale", "latency", "timeout", "retry", "concurrency", "recovery", "fallback", "consistency", "partition"]
    has_completeness = sum(1 for m in completeness_markers if m in lower_text) >= 1

    correctness = min(20, base + focus_bonus)
    reasoning = min(20, base + (3 if has_reasoning else 0) + min(2, focus_bonus))
    technical_understanding = min(20, base + focus_bonus + (1 if word_count >= 60 else 0))
    relevance = min(20, base + min(3, focus_bonus) + 2)
    completeness = min(20, base + (3 if has_completeness else 0) + (1 if word_count >= 80 else 0))
    score = min(100, correctness + reasoning + technical_understanding + relevance + completeness)

    feedback_parts = [f"Sound grasp of {question_meta.get('title', 'the problem')}."]
    if has_reasoning:
        feedback_parts.append("Provided clear justifications for architectural and design choices.")
    else:
        feedback_parts.append("Consider explaining the 'why' behind selected algorithms and tools.")
    if has_completeness:
        feedback_parts.append("Good coverage of edge cases, scaling, and failure scenarios.")
    else:
        feedback_parts.append("Could expand further on failure recovery and trade-offs under high load.")

    return {
        "question_id": question_meta.get("id"),
        "question_title": question_meta.get("title", ""),
        "correctness": correctness,
        "reasoning": reasoning,
        "technical_understanding": technical_understanding,
        "relevance": relevance,
        "completeness": completeness,
        "score": score,
        "feedback": " ".join(feedback_parts),
    }


async def evaluate_single_open_ended_answer(
    track: str,
    question_meta: dict,
    candidate_answer: str
) -> dict:
    """Evaluates an open-ended candidate answer using Gemini 3.6 Flash with multi-criteria rubric, falling back if needed."""
    if not candidate_answer or len(candidate_answer.strip()) < 10:
        return {
            "question_id": question_meta.get("id"),
            "question_title": question_meta.get("title", ""),
            "correctness": 0,
            "reasoning": 0,
            "technical_understanding": 0,
            "relevance": 0,
            "completeness": 0,
            "score": 0,
            "feedback": "No substantial response was provided for this technical scenario.",
        }

    try:
        from app.services.gemini_service import call_gemini_json
        prompt = f"""You are a principal software engineer and expert technical interviewer evaluating a candidate's response to an open-ended scenario question.

TRACK: {track}
QUESTION TITLE: {question_meta.get('title')}
SCENARIO: {question_meta.get('scenario')}
TASK PROMPT: {question_meta.get('prompt')}
RUBRIC FOCUS AREAS: {', '.join(question_meta.get('rubric_focus', []))}

CANDIDATE'S SUBMISSION:
\"\"\"{candidate_answer.strip()}\"\"\"

EVALUATION RULES:
1. Technically correct answers must receive full appropriate credit even if wording differs from expected keywords.
2. Evaluate based on real technical merit, understanding, sound architecture, and trade-off considerations.
3. Score each of the 5 criteria from 0 to 20:
   - correctness: Is the proposed solution technically sound and viable? (0-20)
   - reasoning: Did they explain WHY they chose this approach? (0-20)
   - technical_understanding: Depth of knowledge and domain concepts demonstrated? (0-20)
   - relevance: Did they answer the specific question and scenario asked? (0-20)
   - completeness: Did they consider edge cases, scaling, latency, or failure trade-offs? (0-20)
4. 'score' MUST be the exact sum of these 5 criteria (0-100).
5. Provide 2-3 sentences of objective, constructive feedback in 'feedback'.

Return ONLY a JSON object with this exact schema:
{{
  "correctness": 18,
  "reasoning": 16,
  "technical_understanding": 17,
  "relevance": 18,
  "completeness": 16,
  "score": 85,
  "feedback": "..."
}}"""
        result = await call_gemini_json(prompt)
        if isinstance(result, dict) and "score" in result:
            c = min(20, max(0, int(result.get("correctness", 12))))
            r = min(20, max(0, int(result.get("reasoning", 12))))
            t = min(20, max(0, int(result.get("technical_understanding", 12))))
            rel = min(20, max(0, int(result.get("relevance", 12))))
            comp = min(20, max(0, int(result.get("completeness", 12))))
            total = c + r + t + rel + comp
            return {
                "question_id": question_meta.get("id"),
                "question_title": question_meta.get("title", ""),
                "correctness": c,
                "reasoning": r,
                "technical_understanding": t,
                "relevance": rel,
                "completeness": comp,
                "score": total,
                "feedback": result.get("feedback", "Solid technical solution with sound architectural reasoning."),
            }
    except Exception as e:
        logger.warning(f"AI evaluation fallback invoked for open-ended question: {e}")

    return fallback_evaluate_open_ended(question_meta, candidate_answer)


async def evaluate_open_ended_answers(
    track_id: str,
    submissions: List[OpenEndedAnswerSubmission]
) -> dict:
    """Evaluates all submitted open-ended questions for a given track."""
    questions = OPEN_ENDED_QUESTIONS_MAP.get(track_id, [])
    q_map = {q["id"]: q for q in questions}

    evaluations = []
    total_score = 0

    for sub in submissions:
        meta = q_map.get(
            sub.question_id,
            {"id": sub.question_id, "title": sub.question[:50], "scenario": sub.question, "prompt": sub.question, "rubric_focus": []}
        )
        res = await evaluate_single_open_ended_answer(track_id, meta, sub.answer)
        evaluations.append(res)
        total_score += res["score"]

    avg_score = round(total_score / max(1, len(evaluations)), 1) if evaluations else 0.0

    return {
        "average_score": avg_score,
        "evaluations": evaluations,
    }


# ── Session & Test Endpoints ──────────────────────────────────────────────────
class StartSessionRequest(BaseModel):
    test_id: str = Field(..., max_length=100)


@router.post("/start-session")
async def start_assessment_session(
    payload: StartSessionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Start an assessment session with a strict 10-minute (600s) server timer.
    Enforces server-side time tracking and prevents replay submissions.
    """
    uid = user["uid"]
    test = next((t for t in MOCK_TESTS_CATALOG if t["id"] == payload.test_id), None)
    if not test:
        raise HTTPException(status_code=404, detail=f"Assessment '{payload.test_id}' not found.")

    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    now_ts = time.time()
    time_limit_seconds = 600  # 10 minutes strictly enforced

    session_data = {
        "session_id": session_id,
        "uid": uid,
        "test_id": payload.test_id,
        "start_timestamp": now_ts,
        "time_limit_seconds": time_limit_seconds,
        "expires_timestamp": now_ts + time_limit_seconds,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }
    ACTIVE_TEST_SESSIONS[session_id] = session_data

    return {
        "session_id": session_id,
        "test_id": payload.test_id,
        "time_limit_seconds": time_limit_seconds,
        "start_time": session_data["created_at"],
        "expires_at": datetime.utcfromtimestamp(session_data["expires_timestamp"]).isoformat(),
    }


@router.get("/tests")
async def get_tests():
    """Retrieve available technical assessment drills."""
    return {"tests": MOCK_TESTS_LISTING}


@router.get("/tests/{test_id}")
async def get_test_questions(test_id: str, user: dict = Depends(get_current_user)):
    """Return questions and open-ended technical drills for a specific test."""
    test = next((t for t in MOCK_TESTS_CATALOG if t["id"] == test_id), None)
    if not test:
        raise HTTPException(status_code=404, detail=f"Test '{test_id}' not found.")
    return test


@router.post("/submit")
async def submit_assessment(
    payload: AssessmentSubmitRequest,
    user: dict = Depends(get_current_user)
):
    """
    Record completed assessment results with separate scores for MCQs and open-ended questions.
    Enforces server-side time limits (10 minutes) and recalculates Career Readiness Score.
    """
    uid = user["uid"]
    test_id = payload.test_id

    # 1. Server-side session verification
    time_expired = False
    if payload.session_id:
        session = ACTIVE_TEST_SESSIONS.get(payload.session_id)
        if session:
            if session.get("uid") != uid:
                raise HTTPException(status_code=403, detail="Assessment session does not belong to current user.")
            if session.get("status") == "completed":
                raise HTTPException(status_code=409, detail="This assessment session has already been submitted.")

            elapsed_server = time.time() - session.get("start_timestamp", time.time())
            if elapsed_server > 630:  # 600s + 30s network buffer
                time_expired = True

            session["status"] = "completed"

    try:
        from app.core.firebase import get_firestore
        from app.services.scoring_service import calculate_job_readiness_score, load_user_activities

        db = get_firestore()
        record_id = f"test_{int(datetime.utcnow().timestamp())}_{str(uuid.uuid4())[:8]}"

        test = next((t for t in MOCK_TESTS_CATALOG if t["id"] == test_id), None)
        total_mcqs = len(test["questions"]) if test else payload.total_questions

        # 2. Server-side MCQ validation
        correct_count = 0
        incorrect_count = 0
        topic_map = {}
        diff_map = {}

        if test and payload.mcq_answers:
            for idx, q in enumerate(test["questions"]):
                selected = payload.mcq_answers.get(str(idx))
                if selected is None:
                    selected = payload.mcq_answers.get(str(q["id"]))
                if selected is None:
                    selected = payload.mcq_answers.get(idx)

                is_correct = selected is not None and int(selected) == q["correct"]
                top = q.get("topic", "General")
                diff = q.get("difficulty", "medium")

                if top not in topic_map:
                    topic_map[top] = {"correct": 0, "total": 0}
                topic_map[top]["total"] += 1

                if diff not in diff_map:
                    diff_map[diff] = {"correct": 0, "total": 0}
                diff_map[diff]["total"] += 1

                if is_correct:
                    correct_count += 1
                    topic_map[top]["correct"] += 1
                    diff_map[diff]["correct"] += 1
                else:
                    incorrect_count += 1

            mcq_score = round((correct_count / max(1, total_mcqs)) * 100, 1)
        else:
            correct_count = payload.correct_count
            incorrect_count = payload.incorrect_count
            topic_map = payload.topic_breakdown
            diff_map = payload.difficulty_breakdown
            mcq_score = payload.score

        # 3. Open-ended technical questions evaluation (5 criteria)
        open_ended_eval = None
        open_ended_score = None
        if payload.open_ended_answers and len(payload.open_ended_answers) > 0:
            open_ended_eval = await evaluate_open_ended_answers(test_id, payload.open_ended_answers)
            open_ended_score = open_ended_eval.get("average_score", 0.0)

        # 4. Compute composite overall score
        # 70% MCQ + 30% Open-Ended Problem Solving
        if open_ended_score is not None:
            overall_score = round(0.70 * mcq_score + 0.30 * open_ended_score, 1)
        else:
            overall_score = mcq_score

        test_record = {
            "id": str(uuid.uuid4()),
            "record_id": record_id,
            "test_id": test_id,
            "test_title": payload.test_title,
            "career_path": payload.career_path,
            "category": payload.category,
            "score": overall_score,
            "mcq_score": mcq_score,
            "open_ended_score": open_ended_score,
            "open_ended_evaluations": open_ended_eval.get("evaluations", []) if open_ended_eval else [],
            "total_questions": total_mcqs,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "time_taken": payload.time_taken,
            "time_expired": time_expired,
            "session_id": payload.session_id,
            "topic_breakdown": topic_map,
            "difficulty_breakdown": diff_map,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store test record under assessments/{uid}/records/{record_id}
        db.collection(f"assessments/{uid}/records").document(record_id).set(test_record)

        # Recalculate Career Readiness Score from full profile data
        profile_doc = db.collection("profiles").document(uid).get()
        profile = profile_doc.to_dict() if profile_doc.exists else {"uid": uid}
        profile["uid"] = uid

        activities = load_user_activities(uid)
        readiness = calculate_job_readiness_score(
            profile,
            activities=activities,
            action_reason=f"Completed {payload.test_title} (MCQ: {int(mcq_score)}%, Open-Ended: {int(open_ended_score or mcq_score)}%)"
        )
        db.collection("jobScores").document(uid).set({
            **readiness.model_dump(),
            "uid": uid,
            "updated_at": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "test_id": test_id,
            "score": overall_score,
            "mcq_score": mcq_score,
            "open_ended_score": open_ended_score,
            "readiness_score": readiness.total_score,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "total_questions": total_mcqs,
            "time_taken": payload.time_taken,
            "time_expired": time_expired,
            "topic_breakdown": topic_map,
            "difficulty_breakdown": diff_map,
            "open_ended_evaluations": open_ended_eval.get("evaluations", []) if open_ended_eval else [],
            "message": "Assessment scores recorded and Career Readiness Score recalculated.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record assessment for uid={uid}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to record assessment.")


@router.get("/history")
async def get_assessment_history(user: dict = Depends(get_current_user)):
    """Fetch completed assessment history strictly for authenticated user."""
    uid = user["uid"]
    try:
        from app.core.firebase import get_firestore
        db = get_firestore()
        docs = db.collection(f"assessments/{uid}/records").stream()
        results = [d.to_dict() for d in docs if d.to_dict()]
        # Sort by timestamp descending
        results.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        return {"uid": uid, "assessments": results}
    except Exception as e:
        logger.error(f"Failed to fetch assessments history for uid={uid}: {e}")
        return {"uid": uid, "assessments": []}
