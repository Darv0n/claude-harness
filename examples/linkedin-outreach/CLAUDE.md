# LinkedIn Outreach Operating System

## Purpose
Automated LinkedIn outreach pipeline: research prospects, score against ICP,
generate personalized sequences, track campaigns, and learn from results.

## ICP Matrix

| Tier | Criteria | Sequence Length | Personalization |
|------|----------|-----------------|-----------------|
| Whale | C-suite, 500+ employees, target vertical, budget signals | 5 touches | Deep research, custom angles |
| High | Director+, 100+ employees, adjacent vertical | 4 touches | Role-specific, industry hooks |
| Mid | Manager+, 50+ employees, broad fit | 3 touches | Template + personalization layer |
| Low | Individual contributor, small company | 2 touches | Light template, volume play |

## Voice Engine

### Rules
- Mirror the prospect's communication style (formal/casual detected from profile)
- Never use banned phrases: "synergy", "leverage", "circle back", "touch base"
- Specificity over flattery: reference specific projects/posts, not generic praise
- Mobile-first: messages must be readable in 3 scroll-lengths on mobile

### Observation Points
- LinkedIn post tone and frequency
- About section language style
- Recommendation language patterns
- Content engagement patterns

## Campaign State Machine

```
NEW → RESEARCHED → SCORED → SEQUENCED → SENT → REPLIED → CONVERTED
                                          │        │
                                          ▼        ▼
                                       BOUNCED   DECLINED
                                          │
                                          ▼
                                       ARCHIVED
```

## Quality Gates

1. **Language Match**: outreach tone must match prospect's detected communication style
2. **Template Test**: message must not feel templated (zero-template energy)
3. **Specificity Test**: must reference at least one specific detail from research
4. **Mobile Preview**: first 2 lines must hook on mobile preview
5. **ICP Alignment**: sequence length/depth must match tier

## Research Schema (per prospect)

```yaml
name: string
title: string
company: string
company_size: string
industry: string
icp_tier: Whale | High | Mid | Low
icp_score: 0-100
linkedin_url: string
recent_posts: string[]
about_summary: string
communication_style: formal | casual | technical | executive
pain_points: string[]
mutual_connections: string[]
engagement_hooks: string[]
```

## Workflows

### /research [LinkedIn URL]
1. Extract profile data from URL
2. Research company and industry context
3. Analyze communication style from posts/about
4. Score against ICP matrix
5. Save dossier to memory/prospects/

### /outreach [prospect name]
1. Read prospect dossier from memory
2. Determine sequence length from ICP tier
3. Generate personalized messages per touch
4. Apply quality gates (language, template, specificity, mobile)
5. Save sequence to memory/campaigns/

### /pipeline
1. Read all active campaigns from memory
2. Display by stage (researched, sequenced, sent, replied)
3. Calculate conversion metrics
4. Flag stale sequences for follow-up

## Rules
1. Never send without quality gate pass
2. Always research before outreach — no cold templates
3. Respect prospect's communication style — mirror, don't impose
4. Track everything — memory is the competitive advantage
5. Learn from responses — update patterns after every reply
