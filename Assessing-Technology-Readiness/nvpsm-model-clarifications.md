# NVPSM Model: Clarifications & Philosophy

## The Core Insight: It's About the **Transitions**, Not the Checkpoints

The NVPSM model (Novelty → Viability → Practicality → Sustainability → Maintainability) is fundamentally about describing **what kind of work is being done** on a feature, not what stage it has "achieved."

### Key Mental Model

❌ **Not this:** "Our feature is at Sustainability level 7/9"
✅ **Instead:** "We're taking a viable feature and working to make it practical for production use"

The model describes the **nature of the work** happening in the transition space:

```
Novelty ----[experimental work]----> Viability ----[hardening work]----> Practicality
         ----[operationalizing]----> Sustainability ----[operations/gardening]----> Maintainability
```

## Scope: Feature Quality, Not Business Maturity

### What NVPSM Describes
✅ **The status and quality of a particular technical solution/feature**
- Is this feature idea proven yet?
- Can this feature run reliably in production?
- Are we maintaining and securing this feature?

### What NVPSM Does NOT Describe
❌ **Business maturity, market validation, or organizational capability**
- Commercial viability / market fit
- Revenue generation
- Team organizational maturity
- Business model validation

**Distinction:** This is about the **engineering solution**, not the business around it.

A feature can be in "Sustainability→Maintainability" work even if the business is failing. Conversely, a feature might be in "Novelty→Viability" experimentation while the business is highly mature.

---

## Where Traditional "Gaps" Actually Live in NVPSM

### 1. Deployability → Part of **Sustainability**

**Rationale:** Sustainability means the feature is **robust enough to operate in a deployed/production environment**.

**Work in Practicality → Sustainability transition:**
- Making deployment reliable and repeatable
- Building CI/CD pipelines
- Implementing rollback capabilities
- Creating deployment runbooks
- Establishing deployment safety (blue-green, canary, etc.)

**Exit indicator:** When the feature can be deployed and run stably in production with acceptable operational burden.

---

### 2. Observability → Part of **Maintainability**

**Rationale:** Maintainability isn't just about fixing bugs. It's about **operations and running the software** - like the maintenance crew of a building.

**Work in Sustainability → Maintainability transition:**
- Implementing comprehensive logging
- Setting up metrics and dashboards
- Creating distributed tracing
- Building alerting systems
- Establishing incident response procedures
- Creating operational documentation

**The maintenance crew needs eyes on the system** to do their job.

---

### 3. Security → Part of **Maintainability**

**Rationale:** Security is a **continuous act, like gardening**. It's not a one-time gate you pass through.

**Work in Maintainability:**
- Patching vulnerabilities as they're discovered
- Rotating credentials and certificates
- Monitoring for security incidents
- Updating dependencies for security fixes
- Responding to new threat intelligence
- Conducting regular security reviews

**Mental model:** Just like a garden needs continuous weeding, watering, and pruning, software needs continuous security attention.

---

### 4. Performance & Scalability → Depends on the Transition

**Performance considerations appear throughout:**

- **Viability → Practicality**: Does it perform well enough to be usable?
- **Practicality → Sustainability**: Can it handle production load and scale appropriately?
- **Sustainability → Maintainability**: Ongoing performance optimization and efficiency improvements

Performance isn't a separate dimension - it's a **quality attribute** evaluated differently at each transition.

---

### 5. Integration & Interoperability → Part of **Practicality**

**Rationale:** Practicality means the feature works in the real world with real systems.

**Work in Viability → Practicality transition:**
- Integrating with existing systems and APIs
- Ensuring compatibility with the ecosystem
- Managing dependencies properly
- Building stable interfaces for others to use

**Exit indicator:** The feature plays well with its environment.

---

### 6. Quality Assurance & Testing → Woven Throughout

**Testing evolves with each transition:**

- **Novelty → Viability**: Does it work at all? (Manual testing, experimentation)
- **Viability → Practicality**: Does it work reliably? (Automated tests, edge cases)
- **Practicality → Sustainability**: Does it work in production? (Integration tests, load tests)
- **Sustainability → Maintainability**: Does it keep working? (Regression tests, monitoring)

---

## What This Model Actually Measures

### The Model Answers: "What kind of work are we doing on this feature?"

**Phase 1: Novelty → Viability**
- **Question:** "Can we make this idea actually work?"
- **Work happening:** Prototyping, experimentation, proof-of-concept
- **Uncertainty:** Does the approach even work?
- **Success criteria:** Demonstrated that the core idea functions

**Phase 2: Viability → Practicality**
- **Question:** "Can we make this work reliably in the real world?"
- **Work happening:** Hardening, edge case handling, integration, error handling
- **Uncertainty:** Will it break in production? Does it handle reality?
- **Success criteria:** Works robustly with real data, real users, real integrations

**Phase 3: Practicality → Sustainability**
- **Question:** "Can we run this in production without it falling over?"
- **Work happening:** Operationalizing, deployment automation, making it resilient
- **Uncertainty:** Can we deploy and run this sustainably?
- **Success criteria:** Deployed, stable, manageable operational burden

**Phase 4: Sustainability → Maintainability**
- **Question:** "Can we keep this running and healthy over time?"
- **Work happening:** Operations, monitoring, security patching, optimization, gardening
- **Uncertainty:** Will this become a maintenance nightmare?
- **Success criteria:** Low toil, observable, secure, team can maintain it

---

## The "In Between" is Where the Work Lives

### Example: Authentication Feature Journey

**Early days (Novelty → Viability):**
- "We're experimenting with WebAuthn for passwordless auth"
- Work: Building a prototype, testing browser compatibility
- State: It might work, still proving the concept

**Getting real (Viability → Practicality):**
- "We've proven WebAuthn works, now we're hardening it for production"
- Work: Adding fallback mechanisms, handling edge cases, integration with existing user DB
- State: Core functionality proven, making it production-grade

**Going live (Practicality → Sustainability):**
- "We're operationalizing WebAuthn authentication"
- Work: Building deployment pipeline, creating rollback procedures, load testing
- State: Making it deployable and sustainable to run

**Long-term (Sustainability → Maintainability):**
- "We're maintaining and evolving our WebAuthn system"
- Work: Monitoring auth success rates, patching vulnerabilities, updating specs
- State: Gardening the system, keeping it healthy

---

## What Makes NVPSM Different

### Compared to Other Frameworks

**Traditional TRL/Maturity Models:**
- Focus: "What level have you achieved?"
- Mindset: Checkpoints and gates
- Output: A number (TRL 7, CMMI Level 3)

**NVPSM Model:**
- Focus: "What kind of work are you doing?"
- Mindset: Continuous transitions and evolution
- Output: A description of current work phase

**Key Difference:** NVPSM acknowledges that features don't stay static. A feature in "Maintainability" can regress and need "Practicality" work again if requirements change or bitrot sets in.

---

## Implications for Quantification

### What Should Be Measured?

Since NVPSM describes the **nature of work**, metrics should capture:

1. **Transition indicators** - What signals that work is shifting from one phase to another?
2. **Work distribution** - What % of effort is going into each type of work?
3. **Regression indicators** - When does a feature slip backward?
4. **Time in phase** - How long has the feature been in this work phase?

### Example Metrics

**Novelty → Viability:**
- Experiment velocity (experiments per week)
- Prototype iteration count
- Proof-of-concept success indicators

**Viability → Practicality:**
- Test coverage growth
- Bug fix rate
- Integration completeness

**Practicality → Sustainability:**
- Deployment success rate
- Operational incident rate
- Runbook completeness

**Sustainability → Maintainability:**
- Mean time between incidents (MTBI)
- Security patch frequency
- Toil hours per week
- Observability coverage

---

## Open Questions

### 1. Can work happen in multiple phases simultaneously?

**Example:** A feature might be:
- 80% in Maintainability (running smoothly)
- 20% in Viability→Practicality (adding a new sub-feature)

**Question:** Is this:
- A. A single feature in a mixed state?
- B. Two features (existing + new) in different states?
- C. A feature with sub-components in different states?

### 2. How do you handle rework?

**Scenario:** A feature reaches Maintainability, then requirements change significantly.

**Question:** Is this:
- Regression back to Practicality→Sustainability?
- A new Novelty→Viability cycle for the changed requirements?
- Evolution within Maintainability?

### 3. What about libraries vs. services vs. products?

**Observation:** Different software types might have different transition patterns.

**Examples:**
- **Library:** Might go Novelty→Viability→Practicality→Maintainability (skip Sustainability?)
- **Service:** Full cycle through all phases
- **Internal tool:** Might skip Sustainability and jump to Maintainability?

**Question:** Are there different "tracks" through NVPSM for different software types?

### 4. How granular is a "feature"?

**Question:** Is a "feature":
- A single user-facing capability? (e.g., "Export to PDF")
- An entire system? (e.g., "Authentication system")
- A component? (e.g., "Rate limiter")
- Variable depending on context?

### 5. What triggers transitions between phases?

**Question:** What causes work to shift from one phase to another?
- Time-based? (After N weeks in Viability work, move to Practicality?)
- Criteria-based? (When metrics hit thresholds, transition occurs?)
- Decision-based? (Team decides to shift focus?)
- Emergent? (Nature of work naturally evolves?)

---

## Next Steps for Model Development

### 1. Define Transition Criteria
For each transition, establish:
- **Entry signals:** What indicates this work phase is beginning?
- **Characteristic activities:** What does work in this phase look like?
- **Exit signals:** What indicates readiness to shift to next phase?

### 2. Develop Measurement Framework
- What metrics capture the nature of work in each phase?
- How do you quantify "% of effort" in each phase?
- What leading indicators predict phase transitions?

### 3. Handle Edge Cases
- Simultaneous multi-phase work
- Rework and regression
- Different software types (library, service, product)
- Feature granularity definitions

### 4. Validate Against Real Projects
- Apply NVPSM to actual features in development
- Does the model accurately describe the work being done?
- What adjustments are needed based on reality?

### 5. Build Tooling
- How do teams track which phase(s) their features are in?
- Dashboards showing work distribution across phases?
- Alerts when features stall in a phase too long?

---

## The Gardening Metaphor

The NVPSM model is ultimately about **software gardening**, not construction:

**Construction mindset:** Build it, finish it, done.
**Gardening mindset:** Plant, nurture, maintain, continuously tend.

- **Novelty → Viability:** Finding seeds that can germinate
- **Viability → Practicality:** Getting the plant established and growing
- **Practicality → Sustainability:** Building a resilient garden ecosystem
- **Sustainability → Maintainability:** Continuous weeding, watering, pruning, protecting

Software is a garden, not a building. NVPSM reflects that reality.
