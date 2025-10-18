# Environmental Blame Filtering Feature

**Date Added**: October 2025  
**Status**: ✅ Fully Implemented and Tested

## Problem Statement

The bot was publishing articles that blame Bitcoin mining for environmental problems, such as:
- "Bitcoin's Thousands of Miners Fuel Emissions Crisis"
- "Farms generate heat pollution and noise locally"
- Articles about "boiling the oceans" and climate crisis blame

These articles frame Bitcoin mining negatively for pollution, emissions, and ecological problems, which is not aligned with the bot's purpose of sharing objective mining industry news.

## Solution

Implemented a comprehensive environmental blame detection system that filters out articles with negative environmental framing while allowing neutral or positive environmental reporting.

### Implementation Details

#### Detection Strategy (Two-Tier Approach)

**1. Environmental Blame Terms Detection**
The system detects environmental criticism keywords:
- `emissions crisis`, `fuel emissions`, `pollution`, `pollut`
- `heat pollution`, `noise pollution`, `environmental damage`
- `environmental crisis`, `climate crisis`
- `boiling the oceans`, `boil the ocean`
- `ecological damage`, `ecological crisis`
- `carbon footprint`, `greenhouse gas`
- `global warming contributor`, `energy waste`
- `wasting energy`, `environmental disaster`
- `environmental harm`, `environmental impact crisis`
- `destroying the environment`, `killing the planet`
- `climate change cause`, `accelerating climate change`

**2. Negative Framing Indicators**
The system detects language that assigns blame:
- `thousands of miners fuel`, `miners fuel`, `mining fuels`
- `farms generate`, `mining generates`, `miners generate`
- `mining causes`, `miners cause`
- `responsible for`, `blamed for`
- `contributes to crisis`, `worsening`
- `devastating`, `harmful`, `damaging`

#### Rejection Criteria

An article is **REJECTED** if:
1. **Both conditions met**: Has 1+ environmental blame terms AND 1+ negative framing indicators
2. **Heavy criticism**: Has 2+ environmental blame terms (indicates primary focus on environmental criticism)

An article is **APPROVED** if:
- It discusses renewable energy adoption positively
- It reports on energy efficiency improvements
- It mentions environmental topics neutrally without blame language
- It focuses on operational or business news

### Code Location

**File**: `core.py`  
**Function**: `_is_bitcoin_relevant()`  
**Lines**: ~1280-1328 (environmental filtering section)

The environmental blame check is positioned **BEFORE** the public mining companies check to ensure that even articles mentioning public miners are rejected if they contain environmental blame.

## Test Coverage

**Test File**: `tests/test_bot.py`  
**Test Function**: `test_environmental_blame_filtering()`

### Test Cases (6 total)

#### Articles REJECTED ❌
1. **Emissions Crisis**: "Bitcoin's Thousands of Miners Fuel Emissions Crisis"
   - Contains: `emissions crisis`, `fuel emissions`, `greenhouse gas`, `environmental damage`
   - Contains: `thousands of miners fuel`, `miners fuel`, `mining generates`, `responsible for`

2. **Pollution Blame**: "Bitcoin Mining Farms Generate Heat Pollution and Noise Locally"
   - Contains: `heat pollution`, `noise pollution`, `environmental damage`
   - Contains: `farms generate`, `mining generates`

3. **Boiling Oceans**: "Bitcoin Mining Is Boiling the Oceans"
   - Contains: `boiling the oceans`, `greenhouse gas`, `carbon footprint`
   - Contains: `mining causes`, `blamed for`

4. **Climate Crisis**: "Bitcoin Mining Worsening Climate Crisis"
   - Contains: `climate crisis`, `greenhouse gas`, `environmental damage`
   - Contains: `mining causes`, `worsening`, `blamed for`

#### Articles APPROVED ✅
5. **Renewable Energy**: "Bitcoin Mining Company Switches to 100% Renewable Energy"
   - Mentions: `renewable energy`, `carbon footprint` (neutral context)
   - No negative framing indicators
   - Positive environmental news

6. **Energy Efficiency**: "Marathon Digital Reports 20% Increase in Energy Efficiency"
   - Mentions: `energy efficiency`, public miner name
   - No environmental blame terms
   - Operational improvement news

## Validation Results

**Core Tests**: 14/14 passing ✅  
**Integration Tests**: 3/3 passing ✅  

All existing tests continue to pass, ensuring no regression in other filtering logic.

## Impact on Public Miner Articles

The filter is positioned **BEFORE** the public mining companies auto-approval check. This means:

- ✅ Articles about public miners with operational/business news are approved
- ❌ Articles about public miners with environmental blame are rejected
- ✅ Example: "Marathon Digital Reports 20% Increase in Energy Efficiency" → APPROVED
- ❌ Example: "Marathon Digital's Mining Operations Fuel Emissions Crisis" → REJECTED

This ensures that even legitimate mining companies are not associated with environmental blame articles.

## Real-World Examples

### Rejected Articles ❌
- "Bitcoin's Thousands of Miners Fuel Emissions Crisis"
- "Bitcoin Mining Farms Generate Heat Pollution and Noise Locally"
- "Bitcoin Mining Is Boiling the Oceans"
- "Bitcoin Mining Worsening Climate Crisis, Report Says"
- "Critics Say Bitcoin Mining Damages Environment"

### Approved Articles ✅
- "Bitcoin Mining Company Switches to 100% Renewable Energy"
- "Marathon Digital Reports 20% Increase in Energy Efficiency"
- "CleanSpark Expands Mining Operations with Solar Power"
- "Hut 8 Partners with Renewable Energy Provider"
- "Bitcoin Mining Industry Explores Sustainable Practices"

## Design Decisions

### Why Two-Tier Detection?
The system requires BOTH environmental blame terms AND negative framing indicators (or 2+ blame terms) to reject an article. This prevents false positives:

- **Neutral reporting**: "Bitcoin mining uses electricity" → No blame language → APPROVED
- **Efficiency news**: "Mining company reduces carbon footprint" → Positive context → APPROVED
- **Environmental blame**: "Mining fuels emissions crisis" → Both conditions met → REJECTED

### Why Before Public Miners Check?
Environmental blame articles should be rejected regardless of whether they mention public mining companies. This ensures:
1. The bot doesn't publish negative environmental narratives
2. Public mining companies aren't associated with blame articles
3. Consistent filtering regardless of article source

### Balanced Approach
The filter allows:
- ✅ Neutral environmental reporting
- ✅ Positive renewable energy news
- ✅ Energy efficiency improvements
- ✅ Operational updates about power usage

The filter rejects:
- ❌ Articles blaming mining for emissions
- ❌ Articles about pollution and environmental damage
- ❌ Articles with "boiling the oceans" rhetoric
- ❌ Heavy-handed environmental criticism

## Maintenance Notes

### Adding New Terms
To add new environmental blame terms or negative framing indicators:

1. Edit `core.py`, function `_is_bitcoin_relevant()`
2. Add terms to `environmental_blame_terms` list (line ~1293)
3. Add phrases to `negative_framing_indicators` list (line ~1307)
4. Add test case to `test_environmental_blame_filtering()` in `tests/test_bot.py`
5. Run tests: `python tests/test_bot.py`

### Adjusting Thresholds
Current thresholds:
- Reject if: 1+ environmental blame terms AND 1+ negative framing
- Reject if: 2+ environmental blame terms (regardless of framing)

To adjust, modify the conditions around line 1318-1326 in `core.py`.

## Performance Impact

**Negligible**: The environmental filtering adds minimal processing overhead:
- Simple string matching operations
- Runs only on articles that pass initial Bitcoin mining checks
- No external API calls or complex computations

## Future Enhancements

Potential improvements for future consideration:
1. **Sentiment analysis**: Use ML-based sentiment detection for more nuanced filtering
2. **Context awareness**: Detect when environmental terms are used in rebuttals or counter-arguments
3. **Allowlist**: Specific phrases that should always pass (e.g., "debunking environmental myths")
4. **Metrics**: Track how many articles are filtered for environmental blame

## References

- **Issue**: Filter articles that blame bitcoin mining for environmental problems
- **Implementation PR**: [Link to PR]
- **Core Logic**: `core.py:1256-1453` (entire `_is_bitcoin_relevant()` function)
- **Tests**: `tests/test_bot.py:177-285` (includes environmental, law enforcement, and crypto filtering tests)
- **Documentation**: `README.md` and `.github/copilot-instructions.md`
