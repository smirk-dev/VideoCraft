# Plotly Histogram Parameter Fix

## Issue Resolved
**Error**: `histogram() got an unexpected keyword argument 'bins'`

## Root Cause
The interactive timeline editor was using matplotlib-style `bins` parameter with Plotly Express `px.histogram()` function. Plotly Express uses different parameter names than matplotlib.

## Parameter Mapping
| Library | Parameter | Example |
|---------|-----------|---------|
| **Matplotlib** | `bins=20` | `plt.hist(data, bins=20)` |
| **Plotly Express** | `nbins=20` | `px.histogram(x=data, nbins=20)` |

## Fix Applied

### File: `src/ui/interactive_timeline_editor.py`
**Line 647**: Changed matplotlib-style parameter to Plotly parameter

```python
# Before:
fig = px.histogram(
    x=confidences,
    bins=20,        # ❌ Invalid for Plotly
    title="Cut Confidence Distribution",
    labels={'x': 'Confidence', 'y': 'Count'}
)

# After:
fig = px.histogram(
    x=confidences,
    nbins=20,       # ✅ Valid for Plotly
    title="Cut Confidence Distribution", 
    labels={'x': 'Confidence', 'y': 'Count'}
)
```

## Context
This error occurred in the cut confidence distribution visualization within the interactive timeline editor analytics section.

## Impact
- ✅ **Analytics Display**: Cut confidence histograms now render correctly
- ✅ **Timeline Editor**: Analytics section works without errors
- ✅ **User Experience**: Smooth visualization of cutting statistics
- ✅ **API Compliance**: Proper Plotly Express parameter usage

## Other Histogram Functions
Verified that other histogram functions in the codebase are correctly implemented:
- ✅ **Scene Detector**: Uses OpenCV `cv2.calcHist()` (different API)
- ✅ **Offline Models**: Uses OpenCV `cv2.calcHist()` (different API)

## Technical Notes
- **Plotly Express**: Uses `nbins` for number of bins
- **Matplotlib**: Uses `bins` for number of bins
- **OpenCV**: Uses different parameter structure entirely (`[8]` for bin count)

This fix ensures consistent visualization functionality across the VideoCraft analytics features.
