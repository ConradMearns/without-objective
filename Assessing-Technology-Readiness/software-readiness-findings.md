# Software Readiness Levels: Research Findings

## Deep Dive: How Software Readiness is Quantified

### 1. System Readiness Level (SRL) - Mathematical Approach

**Origin**: [Sauser et al. (2006)](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=b501c19469fa5d11ada2858f310451b81b3dc61a)

**Quantification Method**:
- SRL is calculated by combining Technology Readiness Level (TRL) with Integration Readiness Level (IRL)
- Uses matrix multiplication: SRL matrix = product of IRL matrix × TRL matrix
- Each matrix element represents readiness of one component with respect to every other component
- Final SRL is converted to 1-9 integer scale

**Three Metrics Computed**:
1. **Component SRL** - readiness of individual components
2. **Composite SRL** - aggregate readiness accounting for integrations
3. **System SRL** - overall system readiness index

**Critical Limitation**: The framework has been criticized as "potentially misleading" because it performs mathematically invalid operations on ordinal data (TRL and IRL are ordinal scales, not interval scales, so arithmetic operations like multiplication are not statistically valid). [Source: MATEC Conference 2018](https://www.matec-conferences.org/articles/matecconf/pdf/2018/18/matecconf_ijcaet-isampe2018_02067.pdf)

---

### 2. Service Readiness Levels (SRL) - Maana Framework

**Origin**: [Maana.io](https://github.com/maana-io/ServiceReadinessLevels) (adapted from NASA TRL for software services)

**Six Maturity Levels**:
1. **IDEA** - Academic papers demonstrating foundational technologies
2. **SMALL SCALE PROTOTYPE** - Proof-of-concept with basic documentation
3. **PROTOTYPE SYSTEM** - Complete prototype with real data and metrics
4. **DEMONSTRATION SYSTEM** - Pre-sales environment with automated deployment
5. **FIRST OF A KIND COMMERCIAL** - Operational in customer environments
6. **GENERAL AVAILABILITY** - Widespread customer adoption and validation

**Eight Assessment Dimensions**:
- Evidence
- Documentation
- Integration
- User Experience
- Testing
- Availability
- Support Infrastructure
- Training/Monitoring (at advanced stages)

**Quantification Approach**: Qualitative validation through progressively rigorous requirements at each level. Movement between levels requires demonstrable evidence in all dimensions.

---

### 3. Application Readiness Level (ARL) - NASA Framework

**Origin**: [NASA Applied Sciences Program](https://appliedsciences.nasa.gov/join-mission/publications-resources/application-readiness-level-metric) (adapted from TRL for applications) | [PDF Documentation](https://carbon.nasa.gov/docs/The%20ARL%20Metric.pdf)

**Structure**: 9-level scale organized into three phases:
- **Phase 1 (ARL 1-3)**: Discovery and feasibility
- **Phase 2 (ARL 4-6)**: Development, testing, and validation
- **Phase 3 (ARL 7-9)**: Integration into partner systems and operational use

**Purpose**: Track application maturity from research (ARL 1) to operational/decision-making ready products (ARL 9)

**Key Metrics**:
- Product maturity assessment
- Application capability measurement
- Integration readiness with partner systems
- Decision-making utility

---

### 4. WorkingMouse Software Readiness Level

**Origin**: [WorkingMouse](https://www.workingmouse.com.au/insights/blogs/reworking-trl-and-irl-for-app-development-software-readiness-level/) (Australian software consultancy)

**12-Stage Framework**:
1. Business model canvas
2. Problem/solution validation
3. Market size/competitive analysis
4. Funded
5. Scoped
6. Developing
7. Testing
8. Minimum Viable Product
9. Sales
10. AI Integration
11. Enhanced Cybersecurity Standards
12. Data Privacy Regulations

**Quantification Approach**: **Qualitative validation milestones** rather than numerical metrics
- Emphasizes 50-100 end-user interviews
- Iterative testing cycles
- Market validation
- Demonstrated scope compliance
- Concrete deliverables at each stage

**Philosophy**: Addresses limitations in both [NASA TRL](https://workingmouse.com.au/innovation/software-readiness-level/) (hardware-centric) and Investment Readiness Level (investor-focused) by focusing on app development lifecycle.

---

### 5. CMMI (Capability Maturity Model Integration)

**Origin**: [Software Engineering Institute, Carnegie Mellon University](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) | [CIO Overview](https://www.cio.com/article/274530/cmmi-explained.html)

**Five Maturity Levels**:
1. **Initial** - Unpredictable, ad-hoc processes
2. **Managed** - Projects planned and executed according to policy
3. **Defined** - Organization-wide process standardization
4. **Quantitatively Managed** - Processes measured and controlled
5. **Optimizing** - Continuous improvement focus

**Quantitative Levels (4 & 5)**:

**Level 4 - Quantitatively Managed**:
- Development processes measured and controlled by quantitative data
- Metrics and statistical indicators drive decision-making
- Predictable processes aligned with stakeholder needs
- Data-driven risk management
- Process deficiency correction based on metrics

**Level 5 - Optimizing**:
- Statistical analysis of common causes of process variation
- Leading indicators used as part of statistically defensible management
- Lower process variability
- Continuous evolution and adaptation

**Key Insight**: CMMI represents organizational process maturity rather than individual product readiness, but provides the infrastructure for quantitative software assessment.

---

### 6. ISO 25010 - Software Quality Model

[ISO 25010 Overview](https://www.researchgate.net/figure/The-ISO-25010-software-quality-standard-from-a-product-standpoint_fig1_317195033)

**Eight Quality Characteristics**:
1. Functional suitability
2. Performance efficiency
3. Compatibility
4. Usability
5. Reliability
6. Security
7. Maintainability
8. Portability

**31 Sub-characteristics** further decompose these dimensions

**Critical Limitation**: ISO 25010 defines WHAT to measure but NOT HOW to measure. It provides a hierarchical taxonomy without operational measurement methods. [Research Paper](https://www.researchgate.net/publication/308848262_Evaluating_Open_Source_Software_Quality_Models_Against_ISO_25010)

**Operational Extensions**: QATCH and similar models attempt to make ISO 25010 operational by defining specific metrics for each characteristic.

---

### 7. DORA Metrics - DevOps Performance Quantification

**Origin**: [DevOps Research and Assessment team](https://typoapp.io/blog/dora-devops-metrics) (now part of Google Cloud)

**Four Core Metrics**:
1. **Deployment Frequency** - How often releases go to production
2. **Lead Time for Changes** - Time from commit to production
3. **Mean Time to Restore (MTTR)** - Recovery time after incidents
4. **Change Failure Rate** - Percentage of changes causing production failures

**Quantification**: All metrics are numerical and time-based, providing objective performance indicators across the software delivery pipeline.

**Performance Tiers**: Organizations are classified as Elite, High, Medium, or Low performers based on metric thresholds.

---

### 8. Production Readiness Frameworks

[Comprehensive Guide - OpsLevel](https://www.opslevel.com/resources/production-readiness-in-depth) | [TechTarget Overview](https://www.techtarget.com/searchsoftwarequality/tip/A-production-readiness-checklist-for-software-development) | [Cortex Best Practices](https://www.cortex.io/post/how-to-create-a-great-production-readiness-checklist)

**Key Components**:

#### A. Observability & Monitoring
- Application Performance Monitoring (APM) tools
- Health check instrumentation
- Functionality, latency, and error rate tracking
- UX metrics calculating user satisfaction scores

#### B. Infrastructure & Scalability
- Server, storage, and networking resource adequacy
- Load balancer configuration
- Capacity planning with demand forecasts
- Resource utilization metrics

#### C. Security
- Vulnerability assessments
- Compliance verification
- Security testing results
- Access control validation

#### D. Ownership & Documentation
- Service owner identification
- Contact methods and escalation paths
- Architecture documentation
- Operational runbooks

#### E. Reliability Metrics
- SLA/SLO/SLI definitions and measurements
- Quarterly performance assessments
- Incident response capabilities

**Google SRE Production Readiness Review (PRR) Specific Metrics**: [SRE Book Chapter](https://sre.google/sre-book/evolving-sre-engagement-model/) | [Finding Landmines](https://cloud.google.com/blog/products/gcp/how-sres-find-the-landmines-in-a-service-cre-life-lessons)
- **Paging Rate**: ≤2 incidents per 12-hour shift (Treynor Maximum)
- **Capacity Planning**: 6-8 quarters historical data + 8 quarters forecast
- **SLA Performance**: Quarterly assessment of major components
- **Resource Efficiency**: QPS, daily active users, utilization ratios

**Modern Approach**: Automated verification through continuous production readiness assessment rather than one-time gate.

---

### 9. Goal/Question/Metric (GQM) Paradigm

**Origin**: [Basili et al. (1994)](https://bminard.github.io/2020/03/goal-question-metric)

**Three-Level Framework**:
1. **Goal** - Characterized by purpose, issue, and viewpoint
2. **Question** - Connect object of measurement to quality issue from specific viewpoint
3. **Metric** - Objective (viewpoint-independent) or subjective (viewpoint-dependent) measures

**Process**:
1. Identify quality/productivity goals
2. Derive questions that define the goal completely
3. Develop metrics to answer each question

**Key Innovation**: Explicit introduction of goal coordinates (viewpoint, purpose, issue, object) over earlier models like McCall's quality factors.

---

### 10. Quantitative Software Reliability & Readiness Index

**Origin**: [IEEE research](https://ieeexplore.ieee.org/document/5137352) (2009 conference paper)

**Novel Approach**: Amalgamates data from entire development lifecycle into unified readiness index:
- Requirements specification
- Project management & resources
- Development & testing
- Audits & assessments
- Stability and reliability metrics
- Technical documentation

**Dual Focus**:
- **Product-oriented parameters**: Actual performance and reliability data
- **Process-oriented parameters**: Quality assurance activities

**Key Innovation**: "Explicit linkage to original performance and reliability requirements" - connects process metrics back to actual product requirements.

**Philosophy**: Move from subjective judgment to quantitative rigor aligned with mature processes like CMMI.

---

## Key Patterns Across Frameworks

### 1. **Ordinal Scales Dominate**
Most frameworks (TRL, SRL, ARL, CMMI) use 1-9 or 1-5 ordinal scales rather than continuous metrics.

### 2. **Multiple Dimensions Required**
No single metric captures readiness. Frameworks either:
- Use multiple related scales (TRL + IRL + MRL)
- Define multiple assessment dimensions (Maana's 8 dimensions)
- Create hierarchical characteristics (ISO 25010's 8 + 31)

### 3. **Context Matters**
Different frameworks optimize for different contexts:
- **NASA/DoD TRL**: Hardware and physical systems
- **ARL**: Scientific applications becoming operational tools
- **Service RL**: Cloud-native microservices
- **DORA**: DevOps pipeline performance
- **Production Readiness**: Operational reliability

### 4. **Quantitative vs. Qualitative Tension**
Sophisticated quantitative metrics exist (DORA, Google SRE) but many frameworks rely on qualitative validation milestones (WorkingMouse, ISO 25010 without operational extensions).

### 5. **Process vs. Product Focus**
- **Process-focused**: CMMI (organizational maturity)
- **Product-focused**: TRL, ARL, Service RL (artifact readiness)
- **Hybrid**: Production Readiness, GQM (both)

---

---

## Additional Resources

### Recent Industry Reports (2024)
- [Cortex: State of Software Production Readiness](https://www.cortex.io/report/the-2024-state-of-software-production-readiness) - Survey of 50 engineering leaders
- [JetBrains Qodana: State of Software Quality](https://lp.jetbrains.com/software-quality-report-2024-by-qodana/) - Survey of 808 developers
- [Katalon: State of Software Quality 2024](https://katalon.com/reports/state-quality-2024) - 4000+ insights on QE trends

### Alternative Readiness Frameworks
- [14 Readiness Level Frameworks (ITONICS)](https://www.itonics-innovation.com/blog/14-readiness-level-frameworks) - Overview of TRL, MRL, SRL, IRL, CRL, DRL
- [KTH Innovation Readiness Level](https://medium.com/@alexanderdrobyshevski/kth-innovation-readiness-level-a-multi-dimensional-framework-for-innovation-maturity-ac8bd72bcaa6) - Multidimensional framework
- [Commercial Readiness Level (CRL)](https://www.tamegon.com/trl-crl-levels) - Market readiness scale

### DevOps Maturity Models
- [Appinventiv: DevOps Maturity Model](https://appinventiv.com/blog/devops-maturity-model/)
- [ICF: 5 Phases of DevOps Maturity](https://www.icf.com/insights/technology/the-5-phases-of-devops-maturity)
- [Planview: DevOps Maturity Model Roadmap](https://www.planview.com/resources/articles/the-devops-maturity-model-a-roadmap-to-continuous-improvement/)

### TRL Criticisms for Software
- [SEI: Beyond Technology Readiness Levels for Software](https://www.sei.cmu.edu/documents/860/2010_005_001_15305.pdf) - Carnegie Mellon workshop report
- [ResearchGate: Applying TRL to Software](https://www.researchgate.net/publication/285403347_642_Applying_Technical_Readiness_Levels_to_Software_New_Thoughts_and_Examples)

### Official TRL Documentation
- [NASA: Technology Readiness Levels](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/)
- [DoD: Technology Readiness Assessment Guidebook (Feb 2025)](https://www.cto.mil/wp-content/uploads/2025/03/TRA-Guide-Feb2025-Cleared.pdf)
- [Wikipedia: Technology readiness level](https://en.wikipedia.org/wiki/Technology_readiness_level)

---

## What's Missing?

### 1. **Validated Multidimensional Software Readiness Framework**
No widely-adopted framework explicitly uses dimensions like:
- Novelty → Viability → Practicality → Sustainability → Maintainability

### 2. **Lifecycle-Spanning Quantitative Model**
Most frameworks focus on either:
- Early stages (TRL 1-6, WorkingMouse stages 1-5)
- Late stages (Production Readiness, DORA)
- Process maturity (CMMI)

None provide integrated quantitative assessment across the entire lifecycle from concept to long-term operation.

### 3. **Software-Native Readiness Levels**
Despite decades of criticism, TRL adaptations remain hardware-centric. True software-native frameworks addressing:
- Code decay over time
- Dependency management
- Technical debt accumulation
- Evolutionary architecture
- API stability

...are still emerging rather than standardized.

### 4. **Temporal Dimension**
Most frameworks are static snapshots. Few account for:
- Software entropy
- Drift from production requirements
- Changing threat landscapes
- Technology obsolescence

### 5. **AI/ML-Specific Readiness**
With increasing AI/ML components, traditional frameworks don't assess:
- Model drift
- Data quality degradation
- Adversarial robustness
- Explainability requirements
- Bias and fairness metrics

---

## Conclusion

Software readiness quantification exists along a spectrum:

**Highly Quantitative**:
- DORA metrics (numerical, time-based)
- Google SRE metrics (paging rate, capacity, SLA %)
- CMMI Level 4/5 (statistical process control)

**Semi-Quantitative**:
- System RL (mathematical but flawed)
- Production Readiness (checklists with metrics)
- GQM (structured derivation of metrics)

**Primarily Qualitative**:
- TRL/ARL (ordinal levels with narrative descriptions)
- Service RL (evidence-based progression)
- WorkingMouse RL (milestone validation)
- ISO 25010 (taxonomy without operationalization)

**Your opportunity**: Create a framework that combines:
1. Clear dimensional progression (your Novelty → Maintainability model)
2. Quantitative metrics at each stage (like DORA)
3. Software-specific concerns (decay, dependencies, technical debt)
4. Lifecycle-spanning perspective (concept through long-term operation)
5. Temporal awareness (readiness as dynamic property, not static state)

No existing framework combines all these elements in a cohesive, validated, software-centric readiness model.
