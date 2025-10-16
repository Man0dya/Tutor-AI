# Question Set Caching Strategy

## Overview

Question generation now implements intelligent caching similar to content generation, storing all generated question sets in a global `generated_questions` collection and reusing them across users when similar requests are made.

## Architecture

### Collections

1. **`generated_questions`** (Global Cache)
   - Stores all generated question sets across all users
   - Used for cache lookups and reuse
   - Not tied to any specific user

2. **`question_sets`** (User-Specific)
   - Stores question sets for individual users
   - Used for user history and retrieval
   - References can point to cached or newly generated questions

## Similarity Matching

### Similarity Basis

The cache key combines:
- `contentId`: Source content document
- `questionCount`: Number of questions
- `questionTypes`: Types of questions (sorted)
- `difficultyDistribution`: Easy/Medium/Hard proportions
- `bloomLevels`: Bloom's taxonomy levels (sorted)

Example:
```
content123|count:5|types:Multiple Choice,Short Answer|bloom:Apply,Remember,Understand|diff:E0.3_M0.5_H0.2
```

### Matching Strategy

1. **Exact Match** (Priority 1)
   - Uses `question_params_hash` (SHA256 of all parameters)
   - Instant reuse if parameters are identical
   - Threshold: 1.0 (perfect match)

2. **Similar Match** (Priority 2)
   - Same `contentId` with similar parameters
   - Token overlap similarity between similarity_basis strings
   - Question count match bonus (+0.1)
   - Threshold: 0.90

3. **No Match**
   - Generate new questions via AI
   - Store in cache for future requests

## Flow Diagram

```
POST /questions/generate
         |
         v
Check generated_questions for exact hash match
         |
    +---------+---------+
    |                   |
   YES                 NO
    |                   |
    v                   v
Return cached      Check for similar match
questions          (same contentId, similar params)
    |                   |
    |              +---------+
    |              |         |
    |             YES       NO
    |              |         |
    |              v         v
    |         Return    Generate new
    |         cached    questions (AI)
    |         set            |
    |              |         v
    |              |    Store in cache
    |              |         |
    +-------+------+---------+
            |
            v
    Store in user's
    question_sets
            |
            v
    Return to user
```

## Benefits

### Speed
- **Cache hit**: ~50-200ms (database lookup only)
- **Cache miss**: ~1-2s (AI generation + storage)
- **Improvement**: 5-10x faster for repeated requests

### Cost Savings
- Avoids redundant Gemini API calls
- Same content + parameters = reuse across all users
- Reduces token consumption significantly

### Consistency
- Same inputs always produce the same quality
- Questions are validated once and reused
- Better pedagogical consistency

## Indices

Database indices for performance:
```python
generated_questions:
  - created_at (desc)
  - contentId (asc)
  - similarity_basis (asc)
  - question_params_hash (asc)
```

## Example Scenarios

### Scenario 1: Exact Reuse
```
User A generates 5 MCQs from Content X (Easy: 30%, Medium: 50%, Hard: 20%)
User B requests same → Cache hit (exact) → Instant return
```

### Scenario 2: Similar Reuse
```
User A generates 5 MCQs from Content X with Bloom levels [Remember, Understand]
User B requests 5 MCQs from Content X with Bloom levels [Remember, Apply]
→ Similar match (90%+ similarity) → Return cached set
```

### Scenario 3: New Generation
```
User A generates 10 Short Answer questions from Content Y
→ No existing cache → Generate new → Store in cache
User B later requests same → Cache hit
```

## Metadata Fields

Cached question sets include:
- `cached`: boolean (true if from cache)
- `cache_match`: "exact" | "similar" | undefined
- `similarity`: float (for similar matches)

## Analytics Events

- `question_generate_request`: New generation started
- `question_generate_reuse`: Cache hit (with match type)
- `question_generate_success`: New set generated and cached

## Configuration

No configuration needed—caching is always enabled for question generation to ensure optimal performance and cost efficiency.
