# hackathon_2025_python_codes
The Python codes for Hackathon.

## 常规

所有功能性API都是POST方法，一般返回一个JSON作为主体。

```JSON
{
    "status": 0,
    "message": "Registered 0 new emails.",
    "data": null
}
```

"status"为"0"代表正常，"1"代表异常。
"message"为服务器提供的消息。
"data"为数据载体。

## 接口

1. 加载所有outlook邮件。

启动后只需要执行一次，就可以收集所有邮件。会辨别邮件是否与金融交易有关以及，但是并不做审核。

**Request:**
url: http://{IP}:{PORT}/funcapp/register_all
method: POST
body: {empty}

**Response**
Content-Type: application/json
response body example: 

```JSON
{
    "status": 0,
    "message": "Registered 0 new emails.",
    "data": null
}
```

2. 获得所有相关邮件。

获得来自于指定邮箱且有关于金融交易的所有邮件。

**Request:**
url: http://{IP}:{PORT}/funcapp/acquire_all
method：POST
body: {empty}

**Response**
Content-Type: application/json
response body example: 

```JSON
{
    "status": 0,
    "message": "Registered all emails.",
    "data": [
        {
            "message_id": 4,
            "entry_id": "0000000005FFFB29341DD444B26E15764D43B1490700599967CA67E6CD4489419592D3AE272400000000010C0000599967CA67E6CD4489419592D3AE272400000160CC5A0000",
            "subject": "the stock transaction for audit",
            "sender": "amonra@126.com",
            "body": "Hi team,\r\n\r\nThe pdf attached if for the audit of my transaction.\r\n\r\nThanks!",
            "status": "NEW",
            "audit_pass": false,
            "audit_judgement": "",
            "created_at": "2025-11-25T12:55:28.816Z",
            "updated_at": "2025-11-25T12:55:28.816Z"
        }
    ]
}
```

3. 获得指定邮件。

按照主键请求邮件信息。

**Request:**
url: http://{IP}:{PORT}/funcapp/acquire_target_email/{message_id}
method：POST
body: {empty}

其中message_id可以从acquire_all接口获取。


**Response**
Content-Type: application/json
response body example: 

```JSON
{
    "status": 0,
    "message": "Email found.",
    "data": {
        "message_id": 4,
        "entry_id": "0000000005FFFB29341DD444B26E15764D43B1490700599967CA67E6CD4489419592D3AE272400000000010C0000599967CA67E6CD4489419592D3AE272400000160CC5A0000",
        "subject": "the stock transaction for audit",
        "sender": "amonra@126.com",
        "body": "Hi team,\r\n\r\nThe pdf attached if for the audit of my transaction.\r\n\r\nThanks!",
        "status": "NEW",
        "audit_pass": false,
        "audit_judgement": ""
    }
}
```


4. 审计指定邮件。

指令智能体审计邮件与附件，并将结果写入数据库。

**Request:**
url: http://{IP}:{PORT}/funcapp/audit_email/{message_id}
method：POST
body: {empty}

其中message_id可以从acquire_all接口获取。


**Response**
Content-Type: application/json
response body example: 

```JSON
{
    "status": 1,
    "message": "Registered all emails.",
    "data": [
        {
            "role": "assistant",
            "content": "",
            "reasoning_content": "Okay, let's start by understanding the user's request. They want me to audit a stock transaction from client Super Dealer via email with message_id=\"4\". The attached PDF has the transaction details. The regulation says each transaction must have a total price under $1000.\n\nFirst, I need to check the email content. The subject is \"the stock transaction for audit\" and the body mentions the attached PDF. The PDF's content shows a transaction: stock_id AAPL, buy, 10 shares, $500 per share. So the total price is 10 * 500 = $5000. Wait, that's way over $1000. That's a red flag.\n\nBut wait, maybe there's a mistake in the PDF. Let me confirm the math again. Shares: 10, price per share: $500. Total is 10*500 = $5000. Definitely exceeds the $1000 limit. So the transaction violates the regulation.\n\nNow, I need to check if there's any other information in the PDF that might affect this. The PDF only lists the transaction details as provided. No other fees or discounts mentioned. So the total is indeed $5000.\n\nThe client's profile might have more info, but since the user didn't provide it, I can only go by the given data. The regulation is clear: total must be under $1000. Therefore, this transaction doesn't meet the criteria.\n\nI should use the add_audit_judgement function to set audit_pass as false and explain that the total price exceeds the limit. No need to call other tools since the PDF's data is sufficient. The email's message_id is 4, so that's the parameter for the function.",
            "extra": {
                "model_service_info": {
                    "status_code": 200,
                    "request_id": "8ecbb135-1590-4ab7-ab0e-424a38d22ee7",
                    "code": "",
                    "message": "",
                    "output": {
                        "text": null,
                        "finish_reason": null,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": "",
                                    "reasoning_content": ""
                                }
                            }
                        ]
                    },
                    "usage": {
                        "input_tokens": 5161,
                        "output_tokens": 456,
                        "total_tokens": 5617,
                        "output_tokens_details": {
                            "reasoning_tokens": 374
                        }
                    }
                }
            }
        },
        {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": "add_audit_judgement",
                "arguments": "{\"message_id\": 4, \"audit_pass\": false, \"audit_judgement\": \"The transaction total price ($5000) exceeds the regulatory limit of $1000. Calculation: 10 shares * $500/share = $5000.\"}"
            },
            "extra": {
                "model_service_info": {
                    "status_code": 200,
                    "request_id": "8ecbb135-1590-4ab7-ab0e-424a38d22ee7",
                    "code": "",
                    "message": "",
                    "output": {
                        "text": null,
                        "finish_reason": null,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": "",
                                    "reasoning_content": ""
                                }
                            }
                        ]
                    },
                    "usage": {
                        "input_tokens": 5161,
                        "output_tokens": 456,
                        "total_tokens": 5617,
                        "output_tokens_details": {
                            "reasoning_tokens": 374
                        }
                    }
                },
                "function_id": "1"
            }
        },
        {
            "role": "function",
            "content": "The judgement has been added to the record.",
            "name": "add_audit_judgement",
            "extra": {
                "function_id": "1"
            }
        },
        {
            "role": "assistant",
            "content": "",
            "reasoning_content": "Okay, let me go through the user's query again to make sure I didn't miss anything. The user provided a PDF with a stock transaction where the client bought 10 shares of AAPL at $500 each. The total comes out to $5000, which is way over the $1000 limit mentioned in the regulations. \n\nWait, the user mentioned that the client's profile should be considered. But in the provided information, there's no detail about the client's profile. Maybe the profile could have exceptions or different limits, but since there's no data given, I have to rely solely on the provided PDF and the regulation stated.\n\nThe tools available include reading files and using the add_audit_judgement function. I already used the PDF's data to calculate the total, which clearly exceeds the limit. No need for web searches here because the transaction details are straightforward. \n\nI should check if there's any possibility of a typo in the PDF. For example, maybe the price per share is $50 instead of $500. But the PDF says 500$, so unless there's an error in the document, the calculation holds. Since I can't assume typos without evidence, the original total stands.\n\nThe response from the tool indicated the judgement was added successfully. The user probably expects a confirmation that the audit was completed and the reason for rejection. So the final answer should reiterate the main point: the total exceeds the allowed limit, hence the transaction is invalid.\n",
            "extra": {
                "model_service_info": {
                    "status_code": 200,
                    "request_id": "47d66d6c-b845-496d-9cb7-dca0b1fc5f5a",
                    "code": "",
                    "message": "",
                    "output": {
                        "text": null,
                        "finish_reason": null,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": "",
                                    "reasoning_content": ""
                                }
                            }
                        ]
                    },
                    "usage": {
                        "input_tokens": 5639,
                        "output_tokens": 383,
                        "total_tokens": 6022,
                        "output_tokens_details": {
                            "reasoning_tokens": 309
                        }
                    }
                }
            }
        },
        {
            "role": "assistant",
            "content": "The transaction has been audited and rejected because the total value ($5000) exceeds the regulatory limit of $1000 per transaction. \n\nAudit result: ❌ Invalid transaction\nReason: Total transaction value (10 shares × $500/share) violates the $1000 ceiling specified in the regulations.",
            "extra": {
                "model_service_info": {
                    "status_code": 200,
                    "request_id": "47d66d6c-b845-496d-9cb7-dca0b1fc5f5a",
                    "code": "",
                    "message": "",
                    "output": {
                        "text": null,
                        "finish_reason": null,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": "",
                                    "reasoning_content": ""
                                }
                            }
                        ]
                    },
                    "usage": {
                        "input_tokens": 5639,
                        "output_tokens": 383,
                        "total_tokens": 6022,
                        "output_tokens_details": {
                            "reasoning_tokens": 309
                        }
                    }
                }
            }
        }
    ]
}
```

* data中是智能体的消息列。

5. 对指定邮件进行回复

就是将审计结果发回给发件人。


**Request:**
url: http://{IP}:{PORT}/funcapp/reply_email/{message_id}
method：POST
body: {empty}

其中message_id可以从acquire_all接口获取。


**Response**
Content-Type: application/json
response body example: 

```JSON
{
    "status": 0,
    "message": "Email replied.",
    "data": {
        "message_id": 4,
        "entry_id": "0000000005FFFB29341DD444B26E15764D43B1490700599967CA67E6CD4489419592D3AE272400000000010C0000599967CA67E6CD4489419592D3AE272400000160CC5A0000",
        "subject": "the stock transaction for audit",
        "sender": "amonra@126.com",
        "body": "Hi team,\r\n\r\nThe pdf attached if for the audit of my transaction.\r\n\r\nThanks!",
        "status": "REPLIED",
        "audit_pass": false,
        "audit_judgement": "The transaction total price ($5000) exceeds the regulatory limit of $1000. Calculation: 10 shares * $500/share = $5000."
    }
}
```

6. 针对邮件与智能体聊天（非流式）

需要前端收集对话历史加入request body，可以有多条消息。用户的role为"user"，智能体为"assistant"。

**Request:**
url: http://{IP}:{PORT}/funcapp/chat/{message_id}
method: POST
body: 

```JSON
[
	{"role": "user", "content": "What is the total value of this transaction."}
]
```

其中message_id可以从acquire_all接口获取。


**Response**
Content-Type: application/json
response body example: 

```JSON
{
    "status": 0,
    "message": "Chat got replied.",
    "data": [
        {
            "role": "assistant",
            "content": "",
            "reasoning_content": "Okay, let's see. The user is asking about the total value of the transaction in the attached PDF. The client is Super Dealer, and their profile says each transaction should be under $1000. The PDF shows a buy transaction for 10 shares of AAPL at $500 each.\n\nFirst, I need to calculate the total value. The number of shares is 10, and the price per share is $500. So multiplying those gives 10 * 500 = $5000. But wait, that's way over the $1000 limit. But maybe there's a mistake here? The price per share is listed as 500$, which might be a typo. If it's $500 per share, then 10 shares would be $5000. But Super Dealer's profile says each transaction should be lower than $1000. So this transaction would be violating that rule. However, I should check if the price is correct. Maybe the PDF has an error. Alternatively, if the price was $50 per share, then 10 shares would be $500, which is under $1000. But the data given in the PDF says 500$. So based on the provided information, the total is $5000. The user might be testing if I catch that the transaction exceeds the client's allowed limit. Therefore, the answer should state the total is $5000, which doesn't meet the client's profile requirement.",
            "extra": {
                "model_service_info": {
                    "status_code": 200,
                    "request_id": "d531da0a-c6de-46ad-9bf1-a1ad9ca6f5bb",
                    "code": "",
                    "message": "",
                    "output": {
                        "text": null,
                        "finish_reason": null,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": "",
                                    "reasoning_content": ""
                                }
                            }
                        ]
                    },
                    "usage": {
                        "input_tokens": 5176,
                        "output_tokens": 403,
                        "total_tokens": 5579,
                        "output_tokens_details": {
                            "reasoning_tokens": 326
                        }
                    }
                }
            }
        },
        {
            "role": "assistant",
            "content": "The total value of the transaction is calculated as follows:\n\n**Shares × Price per share = Total Value**  \n10 shares × $500/share = **$5,000**\n\nHowever, this exceeds the client's profile requirement of transactions being **lower than $1,000**. The transaction violates the client's stated rules.",
            "extra": {
                "model_service_info": {
                    "status_code": 200,
                    "request_id": "d531da0a-c6de-46ad-9bf1-a1ad9ca6f5bb",
                    "code": "",
                    "message": "",
                    "output": {
                        "text": null,
                        "finish_reason": null,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": "",
                                    "reasoning_content": ""
                                }
                            }
                        ]
                    },
                    "usage": {
                        "input_tokens": 5176,
                        "output_tokens": 403,
                        "total_tokens": 5579,
                        "output_tokens_details": {
                            "reasoning_tokens": 326
                        }
                    }
                }
            }
        }
    ]
}
```

* data中是智能体的消息列。


7. 针对邮件与智能体聊天（流式）

流式输出聊天内容。

**Request:**
url: http://{IP}:{PORT}/funcapp/chat_stream/{message_id}
method: POST
body: 

```JSON
[
	{"role": "user", "content": "What is the total value of this transaction."}
]
```

其中message_id可以从acquire_all接口获取。


**Response**
Content-Type: text/plain

输出为非重复纯字串。

```
[THINK]
Okay, let's see. The user wants to know the total value of the transaction from the client Super Dealer. The email provided has an attachment called my_transaction.pdf, which I need to check.

First, I should look at the content of the PDF. The user mentioned that the transaction details are in the file. From the provided text, the transaction has a stock ID AAPL, buy action, 10 shares, and a price per share of $500. So the total value would be shares multiplied by price per share. That's 10 * 500 = $5000. 

But wait, the client's profile says each transaction should be under $1000. This transaction is $5000, which is way over the limit. So the total value is $5000, and it's non-compliant. 

I need to make sure there's no other information in the PDF that affects this calculation. The given data seems straightforward. No other fees or charges mentioned. So the total is indeed $5000. The user's question is just asking for the total value, so the answer is $5000. But also, since it's over the limit, it would fail the audit. But the question is only about the total value, not the audit result yet.
[ANSWER]
The total value of the transaction is calculated as follows:

**Shares × Price per Share = 10 × $500 = $5,000**

This exceeds the client's profile limit of $1,000 per transaction. 

Would you like me to proceed with the audit judgment?
```
