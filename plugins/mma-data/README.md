# FighterAPI: ufc and mma skills

UFC and MMA analysis skills on FighterAPI: game previews, player and team research, and the community's standard metrics, with every number pulled live from the FighterAPI MCP server.

## Skills

- `ufc-card-preview`: Use when the user wants a whole UFC card at a glance rather than one fight.
- `ufc-elo-baseline`: Use when the user wants the rating-based view of UFC fighters, in fan or analyst wording.
- `ufc-fight-preview`: Use when the user wants to know how a UFC, PFL or Bellator fight or card shapes up, in fan or analyst wording.
- `ufc-fighter-profile`: Use when the user asks who a UFC fighter is, how he or she fights, or how he or she wins, in fan or analyst wording.

## Data it sends

The skills call the FighterAPI MCP server at `mcp.fighterapi.com`. Each call sends the tool name and its inputs (teams, players, dates, seasons) with your FighterAPI API key, and returns data. Nothing from your files or conversation is sent beyond what a tool call needs. Calls use credits on your FighterAPI account; a free key at https://fighterapi.com/signup includes monthly credits.

Privacy policy: https://fighterapi.com/privacy

## Install

```
/plugin marketplace add sports-data-hq/sportsdatahq-skills
/plugin install mma-data@sportsdatahq
```

More: https://fighterapi.com/skills. Licence: MIT (see LICENSE).
