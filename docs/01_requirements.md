# 1. Introduction

Clinical documents such as lab reports and clinical study protocols are often lengthy, complex, and time-consuming to review manually. Reviewers and analysts must carefully read these documents to extract key information, which can lead to delays and human error.

This project proposes a document-grounded chatbot system that assists users by extracting key insights and answering questions strictly based on uploaded clinical documents, while ensuring no medical diagnosis or treatment advice is provided.

# 2. Input Source (Document Upload)

The system accepts user-uploaded clinical documents in PDF format, such as:

-> Lab reports
-> Clinical trial protocols
-> Study or investigation reports

The uploaded PDF is the only source of information for the system.

Important Constraints

-> The system has no access to external medical knowledge
-> The system does not use the internet
-> All chatbot responses must be derived from the uploaded document only

# 3. System Overview

The system includes a chatbot that:

-> Reads the uploaded PDF
-> Extracts predefined insights
-> Answers user questions using document content
-> Provides citation or section references where possible
-> The chatbot is insight-limited and operates under strict safety 
   boudaries
   
# 4. User Roles
4.1 Reviewer

Role Description:
A reviewer is responsible for validating and approving extracted insights.

Responsibilities:

-> Upload clinical document PDF
-> Review extracted insights
-> Approve or reject insights
-> Ask clarification questions based on the document

4.2 Analyst

Role Description:
An analyst uses the system to understand the document content efficiently.

Responsibilities:

-> Ask questions related to the uploaded document
-> View approved insights
-> Use chatbot for document clarification

Restrictions:

-> Cannot approve or modify insights

# 5. Chatbot Scope (What the Chatbot CAN Do)

The chatbot is designed to perform the following actions:

Answer questions strictly based on uploaded document content

Summarize sections of the document

Extract predefined insights from the document

Provide descriptive explanations without interpretation

Reference document sections or pages when responding

6. Chatbot Restrictions (What the Chatbot MUST NOT Do)

The chatbot must strictly refuse the following:

Medical diagnosis

Treatment or medication advice

Clinical interpretation of results

Patient-specific guidance

Comparison with external guidelines or standards

Use of knowledge not present in the uploaded document

Refusal Behavior

When refusing a request, the chatbot must:

Clearly state its limitation

Remain polite and neutral

Redirect the user to allowed actions

7. Insight Definition

An insight is defined as a structured piece of information directly extracted from the uploaded document, without adding interpretation, opinion, or medical judgment.

Insights exist to:

Reduce manual reading effort

Highlight important document sections

Support human review and approval

8. Types of Insights Extracted

The system is limited to extracting the following insights:

Document Overview
Basic information about the document type and purpose.

Objectives / Purpose
The stated goal or intent of the document or study.

Population Description
General description of subjects or samples mentioned.

Key Measurements or Tests
Tests, observations, or measurements listed in the document.

Inclusion Criteria (if applicable)
Conditions explicitly stated for inclusion.

Exclusion Criteria (if applicable)
Conditions explicitly stated for exclusion.

Endpoints or Outcomes (if applicable)
Outcomes or results the document aims to measure.

Timeline / Duration
Dates, study duration, or reporting timeline.

Methodology Summary
High-level description of how data was collected.

Safety or Monitoring Description (Descriptive Only)
Reporting or monitoring processes mentioned in the document.

⚠️ No insight includes medical judgment or evaluation.

9. Workflow Summary

User uploads a clinical document PDF

System extracts text from the document

Predefined insights are automatically extracted

Reviewer reviews and approves/rejects insights

Approved insights are stored

Chatbot answers user questions using approved document content

10. Non-Functional Requirements
    Performance

Chatbot responses should be generated within acceptable time limits

PDF upload size must be within system limits

Traceability

Chatbot responses must be traceable to document content

Auditability

Insight approval status must be recorded

Reviewer actions must be logged

11. Success Criteria for Day 1

The Day 1 phase is considered complete when:

Input document source is clearly defined

Chatbot scope and limitations are documented

User roles are clearly identified

Insight concept is clearly explained

No diagnosis or treatment functionality is included

12. Conclusion

This document defines the foundational requirements, scope, and safety boundaries of the system. The focus of Day 1 is to establish clear understanding and constraints before proceeding to system architecture and AI implementation.
