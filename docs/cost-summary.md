# LLM Usage and Cost Summary

## Pricing Assumptions

- Price refer to gemini official website.
- Text Generation and Embedding model have different price.
- This link refer to Text Generation Model `Gemini 3.8 Flash` with standar tier
	https://ai.google.dev/gemini-api/docs/pricing?utm_source=google&utm_medium=cpc&utm_campaign=Cloud-SS-DR-AIS-FY26-global-gsem-1713578&utm_content=text-ad&utm_term=KW_google+ai+studio+pricing&gad_source=1&gad_campaignid=23417416052&gbraid=0AAAAACn9t67mjrp7AVW7tAqMSyomcb45q&gclid=EAIaIQobChMIhZyw-JbBlwMVgYZmAh0W6TMFEAAYASABEgKtcPD_BwE#gemini-3.8-flash
- This link refer to Embbeding Model `gemini-embedding-001`
	https://developers.googleblog.com/gemini-embedding-available-gemini-api/#rate-limits-and-pricing

## Embedding Call - SOP Service
- Based on the link, 1M Token = $0.15.
- 1 token = $0.00000015
- Response usage from embedding is None, but try to calculate it online for the estimation

SOP 1 : token usage = 151 X 1 token price = $0.00002265
SOP 2 : token usage = 95 X 1 token price = $0.00001425
SOP 3 : token usage = 178 X 1 token price = $0.0000267
SOP 4 : token usage = 84 X 1 token price = $0.0000126
SOP 5 : token usage = 123 X 1 token price = $0.00001845
SOP 6 : token usage = 115 X 1 token price = $0.00001725
SOP 7 : token usage = 100 X 1 token price = $0.000015

Total usage for processing SOP document is $0.0001269

## Totals by Case
- Based on the embedding pricing link, 1M Token = $0.15.
- 1 token = $0.00000015
- Based on the Text generation link, 1M Token = $0.75 (until 31 december 2026)
- 1 token input = $0.00000075
- 1 token output = $0.00000375

### Case 001
	- Embedding Token : 509 X embedding price  = $0.00007635
	- Text Generation Token :
		- Prompt : 1949 X input price = $0.00146175
		- Completion : 493 X output price = $0.00184875
		- thinking token : 692 X output price = $0.002595
		- Total Token : 3134
	- Total Cost : $0.00598185

### Case 002
	- Embedding Token : 351 X embedding price = $0.00005265
	- Text Generation Token :
		- Prompt : 1753 X input price = $0.00131475
		- Completion : 541 X output price = $0.00202875 
		- thinking token : 806 X output price = $0.0030225
		- Total Token : 3100
	- Total Cost : $0.00641865

### Case 003
	- Embedding Token : 484 X embedding price = $0.0000726
	- Text Generation Token :
		- Prompt : 1918 X input price = $0.0014385000000000001
		- Completion : 574 X output price = $0.0021525
		- thinking token : 1053 X output price = $0.00394875
		- Total Token : 3545
	- Total Cost : $0.00761235

### Case 004
	- Embedding Token : 482 X embedding price = $0.0000723
	- Text Generation Token :
		- Prompt : 1920 X input price = $0.00144
		- Completion : 701 X output price = $0.00262875
		- thinking token : 1131 X output price = $0.00424125
		- Total Token : 3752
	- Total Cost : $0.0083823

### Case 005
	- Embedding Token : 477 X embedding price = $0.00007155
	- Text Generation Token :
		- Prompt : 1923 X input price = $0.00144225
		- Completion : 630 X output price = $0.0023625
		- thinking token : 985 X output price = $0.00369375
		- Total Token : 3538
	- Total Cost : $0.00757005

### Case 006
	- Embedding Token : 487 X embedding price = $0.00007305
	- Text Generation Token :
		- Prompt : 1927 X input price = $0.0014452500000000001
		- Completion : 480 X output price = $0.0018
		- thinking token : 770 X output price = $0.0028875
		- Total Token : 3177
	- Total Cost : $0.0062058

### Case 007
	- Embedding Token : 471 X embedding price = $0.00007065
	- Text Generation Token :
		- Prompt : 1909 X input price = $0.00143175
		- Completion : 644 X output price = $0.002415
		- thinking token : 686 X output price = $0.0025725
		- Total Token : 3239
	- Total Cost : $0.0064899

### Case 008
	- Embedding Token : 496 X embedding price = $0.0000744
	- Text Generation Token :
		- Prompt : 1944 X input price = $0.001458
		- Completion : 760 X output price = $0.00285
		- thinking token : 1137 X output price = $0.00426375
		- Total Token : 3841
	- Total Cost : $0.00864615

### Case 009
	- Embedding Token : 497 X embedding price = $0.00007455
	- Text Generation Token :
		- Prompt : 1932 X input price = $0.001449
		- Completion : 605 X output price = $0.00226875
		- thinking token : 1164 X output price = $0.004365
		- Total Token : 3701
	- Total Cost : $0.0081573

### Case 010
	- Embedding Token : 541 X embedding price = $0.00008115
	- Text Generation Token :
		- Prompt : 2096 X input price = $0.001572
		- Completion : 858 X output price = $0.0032175
		- thinking token : 1212 X output price = $0.004545
		- Total Token : 4166
	- Total Cost : $0.00941565

## Overall Total

### 1 Cycle Include SOP embedding and 1 set patient case
- SOP Service is `7` times call LLM
- `1` Set patient case is `2` times call LLM. `1` embedding and `1` text generation.
- (SOP) `$0.0001269` + (1 Patient Case 010 Total Cost) `$0.00941565`
- Total Cost : `$0.00954255`

### Exclude SOP, Only calculate for 1 Patient Case 010
- `1` Set patient case is `2` times call LLM. `1` embedding and `1` text generation.
- (Embedding patient case) `$0.00008115` + (Text Generation Total of Completion, Prompt and thinking) `$0.0093345`
- Total Cost : `$0.0093345`
