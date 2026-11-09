# VK Sales-Funnel Bot

An AI-powered lead generation bot for VK (VKontakte) communities. It greets potential clients, answers questions about services using an LLM, qualifies leads through a guided form, and delivers each new lead straight to the business owner.

Built as a B2B automation tool for a small service business.

## The business problem

A small service business gets inquiries through its VK community, but:

- Questions come in at all hours and often go unanswered, so warm leads go cold
- The owner manually re-types the same answers about services and pricing
- There is no structured way to capture a lead's contact details and turn an interested visitor into a real request

The result is lost leads and time spent on repetitive replies instead of on actual deals.

## The solution

A bot that runs the full first-contact funnel automatically:

1. **Greets** the visitor and shows a menu (leave a request / ask a question / pricing)
2. **Answers free-form questions** using Mistral AI, grounded in a system prompt that knows the company's services, pricing, and tone, so it never invents offers that do not exist
3. **Qualifies the lead** through a step-by-step form (name → phone → task), with cancel handling at every step
4. **Delivers the lead instantly** to the owner in a private message, with name, phone, the client's task, and a link to their VK profile

The visitor gets an immediate, on-brand response. The owner gets a clean, ready-to-act lead without lifting a finger.

## How it works

- **Guided funnel (FSM):** a finite-state machine walks the user through the request form one field at a time, so the data collected is structured and complete
- **Conversation memory:** the last 10 messages per user are kept in context so the AI answers coherently, while staying lightweight
- **Hybrid logic:** fixed button flows handle pricing and the request form; everything else is routed to the LLM, so the bot is both reliable and flexible
- **Lead delivery:** completed requests are pushed to the admin in real time, turning a conversation into an actionable lead
- **Resilience:** errors are caught so the bot keeps running instead of crashing on an unexpected message

## Stack

| Layer | Tool |
| --- | --- |
| Language | Python (async) |
| VK integration | vkbottle |
| LLM | Mistral AI (mistral-small) |
| State management | vkbottle FSM (state dispenser) |
| Config & secrets | python-dotenv (.env) |

## Status

Built and fully tested. Ready to deploy to a live VK community.

## What this project demonstrates

- Turning a real business bottleneck (lost leads, repetitive replies) into an automated solution
- Designing a structured data-collection flow, not just a chatbot
- Integrating an LLM with guardrails so it stays on-message
- Closing the loop: a conversation becomes a delivered, actionable lead

## Author

Ekaterina Sarycheva — Prague
Building AI and automation solutions for business.
