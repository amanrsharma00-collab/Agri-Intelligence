#!/usr/bin/env node
/**
 * Agri MCP Server — Node.js Entry Point
 * Bridges Python logic to Claude Desktop via MCP protocol
 *
 * Run: node index.js
 * Install: npm install @modelcontextprotocol/sdk
 */

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { ListToolsRequestSchema, CallToolRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
const { spawn } = require("child_process");
const path = require("path");

// ─────────────────────────────────────────────
// Call Python MCP server functions
// ─────────────────────────────────────────────
function callPythonTool(toolName, params = {}) {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import sys
sys.path.insert(0, '${path.join(__dirname, "src")}')
from agri_mcp_server import run_tool, list_tools
import json

try:
    if '${toolName}' == 'list_tools':
        result = list_tools()
    else:
        result = run_tool('${toolName}', **${JSON.stringify(params)})
    print(json.dumps(result, ensure_ascii=False))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;

    const proc = spawn("python3", ["-c", pythonScript]);
    let output = "";
    let errorOutput = "";

    proc.stdout.on("data", (data) => { output += data.toString(); });
    proc.stderr.on("data", (data) => { errorOutput += data.toString(); });

    proc.on("close", (code) => {
      try {
        resolve(JSON.parse(output.trim()));
      } catch (e) {
        resolve({ error: `Parse error: ${e.message}`, raw: output, stderr: errorOutput });
      }
    });
  });
}

// ─────────────────────────────────────────────
// MCP Server Setup
// ─────────────────────────────────────────────
const server = new Server(
  { name: "agri-mcp-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_mandi_prices",
        description: "Fetch live mandi/market prices for agricultural commodities in Chhattisgarh",
        inputSchema: {
          type: "object",
          properties: {
            commodity: { type: "string", description: "Crop name e.g. paddy, maize, soybean" },
            district: { type: "string", description: "District name in Chhattisgarh" },
            state: { type: "string", description: "State name", default: "Chhattisgarh" }
          }
        }
      },
      {
        name: "get_weather_advisory",
        description: "Get weather data and agricultural advisory for a Chhattisgarh district",
        inputSchema: {
          type: "object",
          properties: {
            district: { type: "string", description: "District name e.g. Raipur, Bastar, Surguja", default: "Raipur" }
          }
        }
      },
      {
        name: "get_agri_schemes",
        description: "Find government schemes matching farmer profile — central + Chhattisgarh state schemes",
        inputSchema: {
          type: "object",
          properties: {
            farmer_type: { type: "string", description: "small / marginal / large", default: "small" },
            crop: { type: "string", description: "Primary crop e.g. paddy, maize, soybean", default: "paddy" },
            district: { type: "string", description: "District in Chhattisgarh", default: "Raipur" }
          }
        }
      },
      {
        name: "get_crop_advisory",
        description: "Get detailed crop-specific advisory for Chhattisgarh conditions",
        inputSchema: {
          type: "object",
          properties: {
            crop: { type: "string", description: "paddy / maize / soybean", default: "paddy" },
            stage: { type: "string", description: "sowing / growing / harvesting", default: "sowing" },
            district: { type: "string", description: "District name", default: "Raipur" }
          }
        }
      },
      {
        name: "assess_distress_risk",
        description: "Assess farmer distress risk combining price, weather and scheme data",
        inputSchema: {
          type: "object",
          required: ["district"],
          properties: {
            district: { type: "string", description: "District name in Chhattisgarh" },
            crop: { type: "string", description: "Primary crop", default: "paddy" },
            landholding_acres: { type: "number", description: "Farm size in acres", default: 2.0 }
          }
        }
      },
      {
        name: "get_district_dashboard",
        description: "Complete agriculture intelligence dashboard for a Chhattisgarh district",
        inputSchema: {
          type: "object",
          properties: {
            district: { type: "string", description: "District name", default: "Raipur" }
          }
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    const result = await callPythonTool(name, args || {});
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ error: error.message })
        }
      ],
      isError: true
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Agri MCP Server running — Connected to Claude Desktop");
}

main().catch(console.error);
