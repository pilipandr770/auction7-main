# Chatbot Setup Guide

This document explains how to set up the chatbot assistant in the auction application.

## Configuration

The chatbot requires OpenAI API credentials to work properly. Follow these steps:

1. Copy the `.env.example` file to create a new `.env` file in the project root:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your OpenAI API credentials:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_ASSISTANT_ID=your_assistant_id_here
   ```
   
   Note: You can create an assistant in the [OpenAI platform](https://platform.openai.com/assistants).

3. Restart the application for the changes to take effect.

## Fallback Mode

If you don't have OpenAI API credentials, the chatbot will work in fallback mode. 
In this mode, it provides basic pre-defined responses and doesn't use AI capabilities.

## Troubleshooting

- If you see a message like "Invalid type for 'assistant_id': expected a string, but got null instead", 
  it means your OpenAI Assistant ID is not configured correctly.
  
- Make sure both `OPENAI_API_KEY` and `OPENAI_ASSISTANT_ID` are properly set in your `.env` file.

- Check the application logs for more detailed error information.
