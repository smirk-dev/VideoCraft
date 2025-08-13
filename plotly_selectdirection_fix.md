# Plotly SelectDirection Fix

## Issue Resolved
**Error**: `Invalid value of type 'builtins.str' received for the 'selectdirection' property of layout Received value: 'horizontal'`

## Root Cause
The interactive timeline editor was using an invalid value for Plotly's `selectdirection` property. Plotly only accepts these enumeration values:
- 'h' (horizontal)
- 'v' (vertical) 
- 'd' (diagonal)
- 'any'

## Fix Applied

### File: `src/ui/interactive_timeline_editor.py`
**Line 285**: Changed invalid value to valid enumeration

```python
# Before:
selectdirection='horizontal'  # ❌ Invalid

# After:  
selectdirection='h'           # ✅ Valid
```

## Impact
- ✅ **Timeline Visualization**: Interactive timeline now displays without Plotly errors
- ✅ **User Experience**: Smooth horizontal selection functionality in timeline editor
- ✅ **Application Stability**: No more Plotly enumeration validation errors

## Technical Details
- **Property**: `selectdirection` in Plotly layout configuration
- **Context**: Interactive video timeline subplot configuration
- **Functionality**: Controls direction of drag selection in timeline visualization
- **Result**: Horizontal selection works as intended with proper Plotly validation

## Verification
- ✅ Plotly configuration validation passes
- ✅ StreamLit application starts without errors
- ✅ Interactive timeline displays correctly
- ✅ Selection functionality works as expected

This fix ensures the interactive timeline editor follows Plotly's API specifications for layout properties.
