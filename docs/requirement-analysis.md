# Requirement Analysis

## 1. Problem Understanding

This app have 2 service:
- SOP Service
	Create this service to handle the SOP Documents and store it to database. Handling multiple file also supported to covering requirement for this test. SOP may have an update in the future, so this system can process new SOP Document that need to upload into `storage/sop` and after that trigger the endpoint to re-generate SOP data vector.
- Assistant Service
	To handle requirement handling multiple patient case, this service only use for upload that document. Uploaded document will be processed into vector before find relevant SOP using vector inside database, this will cover requirement for RAG Process. 

SOP Document will be used for base rules to make AI analyze and also make decission for the patient case. Structured format output and behavior for this assistant will be configure inside the system prompt and user prompt.

## 2. Functional Requirements

Model will follow the instructions about how to response the data given. Because SOP is configured as a part in user prompt, so the behavior itself will following information inside the SOP content. Validate Case ID and Patient ID for each patient case given, Not giving smalltalk on response, and doing medical analysis is some of the behavior.

## 4. Scope

### In Scope

- Multiple document process of SOP
- Real-time data ingestion from uploaded patient case document
- Response with structured JSON

### Out of Scope

- Historical uploaded patient case
- Interface

## 5. Success Criteria

- Read Document, Get Text Content, Chunk Process, run the embedding and inserted to DB with equal row referrence on log data.
- Can support multiple Patient Case in one process. Process it to vector using embeding, find relevant row SOP vector.
- Relevant SOP data and patient case will be joined as user prompt.
- LLM give structured json format as response following the instructions.
- Evidence including SOP file and detail about related field/line.
- inlclude information about inconsistency document with detail.

## 8. Risks and Constraints

- Choose good model by doing test, response speed, response accuration and costs.
- Gather information about how many user will use this service to decide server specification.
- Estimate concurent user, make sure provider limitation request and the model available to that estimation.
