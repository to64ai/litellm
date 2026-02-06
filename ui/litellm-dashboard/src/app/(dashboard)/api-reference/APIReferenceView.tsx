"use client";
import React from "react";
import { Text, Tab, TabGroup, TabList, TabPanel, TabPanels, Grid } from "@tremor/react";
import CodeBlock from "./components/CodeBlock";

interface ApiRefProps {
  proxySettings: {
    PROXY_BASE_URL?: string;
    LITELLM_UI_API_DOC_BASE_URL?: string | null;
  };
}

const APIReferenceView: React.FC<ApiRefProps> = ({ proxySettings }) => {
  let base_url = "<your_proxy_base_url>";
  const customDocBaseUrl = proxySettings?.LITELLM_UI_API_DOC_BASE_URL;
  if (customDocBaseUrl && customDocBaseUrl.trim()) {
    base_url = customDocBaseUrl;
  } else if (proxySettings?.PROXY_BASE_URL) {
    base_url = proxySettings.PROXY_BASE_URL;
  }

  return (
    <>
      <Grid className="gap-2 p-8 h-[80vh] w-full mt-2">
        <div className="mb-5">
          {/* Header row with Contact Admin link on the right */}
          <div className="flex items-center justify-between">
            <p className="text-2xl text-tremor-content-strong dark:text-dark-tremor-content-strong font-semibold">
              OpenAI Compatible Proxy: API Reference
            </p>
            <a
              href="mailto:support@to64.ai?subject=API%20Reference%20Support&body=Hi%20To64%20Team%2C%0A%0AI%20need%20help%20with%20the%20API%20Reference.%0A%0AIssue%20Description%3A%20%0A%0AThank%20you!"
              className="ml-3 shrink-0 inline-flex items-center gap-2 px-3 py-1.5 bg-[#6366f1] hover:bg-[#5558e3] text-white text-sm font-medium rounded-lg transition-colors"
            >
              Contact Admin
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </a>
          </div>

          <Text className="mt-2 mb-2">
            To64 VPA is OpenAI Compatible. This means your API Key works with the OpenAI SDK. Just replace the base_url
            to point to your VPA proxy. Example Below{" "}
          </Text>

          <TabGroup>
            <TabList>
              <Tab>OpenAI Python SDK</Tab>
              <Tab>LlamaIndex</Tab>
              <Tab>Langchain Py</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <CodeBlock
                  language="python"
                  code={`import openai
client = openai.OpenAI(
    api_key="your_api_key",
    base_url="${base_url}" # To64 VPA Proxy is OpenAI compatible
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo", # model to send to the proxy
    messages = [
        {
            "role": "user",
            "content": "this is a test request, write a short poem"
        }
    ]
)

print(response)`}
                />
              </TabPanel>

              <TabPanel>
                <CodeBlock
                  language="python"
                  code={`import os, dotenv

from llama_index.llms import AzureOpenAI
from llama_index.embeddings import AzureOpenAIEmbedding
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext

llm = AzureOpenAI(
    engine="azure-gpt-3.5",               # model_name on To64 VPA proxy
    temperature=0.0,
    azure_endpoint="${base_url}", # To64 VPA proxy endpoint
    api_key="sk-1234",                    # To64 VPA proxy API Key
    api_version="2023-07-01-preview",
)

embed_model = AzureOpenAIEmbedding(
    deployment_name="azure-embedding-model",
    azure_endpoint="${base_url}",
    api_key="sk-1234",
    api_version="2023-07-01-preview",
)

documents = SimpleDirectoryReader("llama_index_data").load_data()
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
index = VectorStoreIndex.from_documents(documents, service_context=service_context)

query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
print(response)`}
                />
              </TabPanel>

              <TabPanel>
                <CodeBlock
                  language="python"
                  code={`from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage

chat = ChatOpenAI(
    openai_api_base="${base_url}",
    model = "gpt-3.5-turbo",
    temperature=0.1
)

messages = [
    SystemMessage(
        content="You are a helpful assistant that im using to make a test request to."
    ),
    HumanMessage(
        content="test from To64 VPA proxy. tell me why it's amazing in 1 sentence"
    ),
]
response = chat(messages)

print(response)`}
                />
              </TabPanel>
            </TabPanels>
          </TabGroup>
        </div>
      </Grid>
    </>
  );
};

export default APIReferenceView;
