import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Card,
  CardContent,
  TextField,
  Button,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Grid,
  CssBaseline,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AssignmentIcon from '@mui/icons-material/Assignment';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Collapse from '@mui/material/Collapse';

const API_BASE = 'http://localhost:8000';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    background: {
      default: '#f5f7fa',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});

function App() {
  // Single classification state
  const [singleUrl, setSingleUrl] = useState('');
  const [singleTemplate, setSingleTemplate] = useState('zero_shot.tpl');
  const [singleResult, setSingleResult] = useState(null);
  const [singleLoading, setSingleLoading] = useState(false);
  const [singleError, setSingleError] = useState('');
  const [singleSuccess, setSingleSuccess] = useState(false);

  // Batch classification state
  const [batchUrls, setBatchUrls] = useState('');
  const [batchTemplate, setBatchTemplate] = useState('zero_shot.tpl');
  const [batchResults, setBatchResults] = useState([]);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchError, setBatchError] = useState('');
  const [batchSuccess, setBatchSuccess] = useState(false);

  // Results lookup state
  const [lookupId, setLookupId] = useState('');
  const [lookupUrl, setLookupUrl] = useState('');
  const [lookupResult, setLookupResult] = useState(null);
  const [lookupResults, setLookupResults] = useState([]);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState('');

  // Admin: List all results state
  const [allResults, setAllResults] = useState([]);
  const [allLoading, setAllLoading] = useState(false);
  const [allError, setAllError] = useState('');

  // Accordion state
  const [expanded, setExpanded] = useState('single');
  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  // Single output collapse
  const [showSingleOutput, setShowSingleOutput] = useState(true);
  // Batch output collapse per row
  const [openBatchRows, setOpenBatchRows] = useState({});
  // Lookup output collapse (single result)
  const [showLookupOutput, setShowLookupOutput] = useState(true);
  // Lookup output collapse per row (by URL)
  const [openLookupRows, setOpenLookupRows] = useState({});
  // All results output collapse per row
  const [openAllRows, setOpenAllRows] = useState({});

  // State for delete by ID
  const [deleteId, setDeleteId] = useState('');
  const [deleteStatus, setDeleteStatus] = useState('');
  const [deleteAllStatus, setDeleteAllStatus] = useState('');

  // Live results auto-refresh
  useEffect(() => {
    const fetchResults = async () => {
      try {
        const res = await fetch(`${API_BASE}/results/all/`);
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        setAllResults(data);
      } catch (err) {
        setAllError('Failed to fetch all results.');
      }
    };
    fetchResults();
    const interval = setInterval(fetchResults, 20000);
    return () => clearInterval(interval);
  }, []);

  // Handlers for single classification
  const handleSingleSubmit = async (e) => {
    e.preventDefault();
    setSingleLoading(true);
    setSingleError('');
    setSingleResult(null);
    setSingleSuccess(false);
    try {
      // Clean and encode the URL properly
      const cleanUrl = singleUrl.trim().replace(/\s+/g, '');
      const res = await fetch(`${API_BASE}/classify/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          url: cleanUrl, 
          template: singleTemplate 
        })
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'API error');
      }
      const data = await res.json();
      setSingleResult(data);
      setSingleSuccess(true);
    } catch (err) {
      setSingleError(err.message || 'Failed to classify.');
    } finally {
      setSingleLoading(false);
    }
  };

  // Handlers for batch classification
  const handleBatchSubmit = async (e) => {
    e.preventDefault();
    setBatchLoading(true);
    setBatchError('');
    setBatchResults([]);
    setBatchSuccess(false);
    try {
      const urls = batchUrls.split('\n').map(u => u.trim()).filter(Boolean);
      const res = await fetch(`${API_BASE}/batch/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls, template: batchTemplate })
      });
      if (!res.ok) throw new Error('API error');
      const data = await res.json();
      setBatchResults(data.results || []);
      setBatchSuccess(true);
    } catch (err) {
      setBatchError('Failed to classify batch.');
    } finally {
      setBatchLoading(false);
    }
  };

  // Handlers for results lookup
  const handleLookupById = async (e) => {
    e.preventDefault();
    setLookupLoading(true);
    setLookupError('');
    setLookupResult(null);
    setLookupResults([]);
    try {
      const res = await fetch(`${API_BASE}/results/${lookupId}`);
      if (!res.ok) throw new Error('Not found');
      const data = await res.json();
      setLookupResult(data);
    } catch (err) {
      setLookupError('Result not found.');
    } finally {
      setLookupLoading(false);
    }
  };

  const handleLookupByUrl = async (e) => {
    e.preventDefault();
    setLookupLoading(true);
    setLookupError('');
    setLookupResult(null);
    setLookupResults([]);
    try {
      const res = await fetch(`${API_BASE}/results/by_url/?url=${encodeURIComponent(lookupUrl)}`);
      if (!res.ok) throw new Error('Not found');
      const data = await res.json();
      setLookupResults(data);
    } catch (err) {
      setLookupError('No results found for this URL.');
    } finally {
      setLookupLoading(false);
    }
  };

  const handleFetchAllResults = async () => {
    setAllLoading(true);
    setAllError('');
    setAllResults([]);
    try {
      const res = await fetch(`${API_BASE}/results/all/`);
      if (!res.ok) throw new Error('API error');
      const data = await res.json();
      setAllResults(data);
    } catch (err) {
      setAllError('Failed to fetch all results.');
    } finally {
      setAllLoading(false);
    }
  };

  // Handlers for toggling
  const handleToggleBatchRow = id => {
    setOpenBatchRows(prev => ({ ...prev, [id]: !prev[id] }));
  };
  const handleToggleLookupRow = id => {
    setOpenLookupRows(prev => ({ ...prev, [id]: !prev[id] }));
  };
  const handleToggleAllRow = id => {
    setOpenAllRows(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Delete a single result by ID
  const handleDeleteResult = async (id) => {
    if (!window.confirm('Are you sure you want to delete this result?')) return;
    try {
      const res = await fetch(`${API_BASE}/results/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      setAllResults(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      alert('Failed to delete result.');
    }
  };

  // Delete all results
  const handleDeleteAllResults = async () => {
    if (!window.confirm('Are you sure you want to delete ALL results? This cannot be undone.')) return;
    try {
      const res = await fetch(`${API_BASE}/results/all/`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete all failed');
      setAllResults([]);
    } catch (err) {
      alert('Failed to delete all results.');
    }
  };

  // Delete a single result by ID (for the new section)
  const handleDeleteById = async (e) => {
    e.preventDefault();
    setDeleteStatus('');
    if (!deleteId) {
      setDeleteStatus('Please enter a result ID.');
      return;
    }
    if (!window.confirm(`Are you sure you want to delete result ${deleteId}?`)) return;
    try {
      const res = await fetch(`${API_BASE}/results/${deleteId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      setDeleteStatus('Result deleted successfully.');
      setDeleteId('');
    } catch (err) {
      setDeleteStatus('Failed to delete result.');
    }
  };

  // Delete all results (for the new section)
  const handleDeleteAllStandalone = async () => {
    setDeleteAllStatus('');
    if (!window.confirm('Are you sure you want to delete ALL results? This cannot be undone.')) return;
    try {
      const res = await fetch(`${API_BASE}/results/all/`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete all failed');
      setDeleteAllStatus('All results deleted successfully.');
    } catch (err) {
      setDeleteAllStatus('Failed to delete all results.');
    }
  };

  // Helper to extract event types and significance from model_output
  const getEventSummary = (model_output) => {
    if (!model_output) return { types: '', relevant: '' };
    let events = [];
    if (Array.isArray(model_output)) {
      events = model_output;
    } else if (model_output.Events) {
      events = model_output.Events;
    }
    const types = events.map(e => e["Event Type"] || e["type"] || '').filter(Boolean).join(', ');
    const relevant = events.map(e => (e["Relevant"] !== undefined ? String(e["Relevant"]) : '')).filter(Boolean).join(', ');
    return { types, relevant };
  };

  const [showIdCol, setShowIdCol] = useState(false);

  // Add new state for prompt type toggle
  const [showPromptType, setShowPromptType] = useState(false);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" color="primary" elevation={2}>
        <Toolbar>
          <AssignmentIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            SEC 8-K Event Classifier
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Accordion expanded={expanded === 'single'} onChange={handleAccordionChange('single')}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Single Filing Classification</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Card elevation={4} sx={{ mb: 2 }}>
              <CardContent>
                <Box component="form" onSubmit={handleSingleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField label="SEC Filing URL" value={singleUrl} onChange={e => setSingleUrl(e.target.value)} required fullWidth />
                  <Select value={singleTemplate} onChange={e => setSingleTemplate(e.target.value)} fullWidth>
                    <MenuItem value="zero_shot.tpl">Zero-Shot</MenuItem>
                    <MenuItem value="cot.tpl">Chain-of-Thought</MenuItem>
                  </Select>
                  <Button type="submit" variant="contained" color="primary" disabled={singleLoading}>
                    {singleLoading ? <CircularProgress size={24} /> : 'Classify'}
                  </Button>
                </Box>
                {singleError && <Alert severity="error" sx={{ mt: 2 }}>{singleError}</Alert>}
                {singleResult && (
                  <Box sx={{ mt: 2, maxHeight: 250, overflow: 'auto' }}>
                    <Alert severity="success">Classification complete!</Alert>
                    <Button size="small" onClick={() => setShowSingleOutput(v => !v)} sx={{ mt: 1 }}>
                      {showSingleOutput ? 'Hide Output' : 'Show Output'}
                    </Button>
                    <Collapse in={showSingleOutput}>
                      <pre style={{ background: '#f4f4f4', padding: 10, marginTop: 10, borderRadius: 4 }}>{JSON.stringify(singleResult, null, 2)}</pre>
                    </Collapse>
                  </Box>
                )}
              </CardContent>
            </Card>
          </AccordionDetails>
        </Accordion>

        <Accordion expanded={expanded === 'batch'} onChange={handleAccordionChange('batch')}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Batch Filing Classification</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Card elevation={4} sx={{ mb: 2 }}>
              <CardContent>
                <Box component="form" onSubmit={handleBatchSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField label="One SEC Filing URL per line" value={batchUrls} onChange={e => setBatchUrls(e.target.value)} multiline minRows={4} required fullWidth />
                  <Select value={batchTemplate} onChange={e => setBatchTemplate(e.target.value)} fullWidth>
                    <MenuItem value="zero_shot.tpl">Zero-Shot</MenuItem>
                    <MenuItem value="cot.tpl">Chain-of-Thought</MenuItem>
                  </Select>
                  <Button type="submit" variant="contained" color="primary" disabled={batchLoading}>
                    {batchLoading ? <CircularProgress size={24} /> : 'Classify Batch'}
                  </Button>
                </Box>
                {batchError && <Alert severity="error" sx={{ mt: 2 }}>{batchError}</Alert>}
                {batchResults.length > 0 && (
                  <Box sx={{ mt: 2, maxHeight: 250, overflow: 'auto' }}>
                    <Alert severity="success">Batch classification complete!</Alert>
                    <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 200 }}>
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>URL</TableCell>
                            <TableCell>Validation</TableCell>
                            <TableCell>Model Output</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {batchResults.map(r => (
                            <TableRow key={r.id}>
                              <TableCell>{r.id}</TableCell>
                              <TableCell sx={{ wordBreak: 'break-all' }}>{r.url}</TableCell>
                              <TableCell>{String(r.validation)}</TableCell>
                              <TableCell>
                                <Button size="small" onClick={() => handleToggleBatchRow(r.id)} sx={{ mb: 1 }}>
                                  {openBatchRows[r.id] ? 'Hide Output' : 'Show Output'}
                                </Button>
                                <Collapse in={!!openBatchRows[r.id] ?? true}>
                                  <pre style={{ maxWidth: 300, overflowX: 'auto', margin: 0 }}>{JSON.stringify(r.model_output, null, 2)}</pre>
                                </Collapse>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </AccordionDetails>
        </Accordion>

        <Accordion expanded={expanded === 'lookup'} onChange={handleAccordionChange('lookup')}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Results Lookup</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Card elevation={4} sx={{ mb: 2 }}>
              <CardContent>
                <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
                  <Grid>
                    <Box component="form" onSubmit={handleLookupById} sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <TextField label="Result ID" value={lookupId} onChange={e => setLookupId(e.target.value)} fullWidth />
                      <Button type="submit" variant="outlined" disabled={lookupLoading}>Lookup by ID</Button>
                    </Box>
                    <Box component="form" onSubmit={handleDeleteById} sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <TextField label="Result ID" value={deleteId} onChange={e => setDeleteId(e.target.value)} fullWidth />
                      <Button type="submit" variant="contained" color="error">Delete by ID</Button>
                    </Box>
                    {deleteStatus && <Alert severity={deleteStatus.includes('success') ? 'success' : 'error'} sx={{ mt: 1 }}>{deleteStatus}</Alert>}
                  </Grid>
                  <Grid>
                    <Box component="form" onSubmit={handleLookupByUrl} sx={{ display: 'flex', gap: 1 }}>
                      <TextField label="SEC Filing URL" value={lookupUrl} onChange={e => setLookupUrl(e.target.value)} fullWidth />
                      <Button type="submit" variant="outlined" disabled={lookupLoading}>Lookup by URL</Button>
                    </Box>
                  </Grid>
                </Grid>
                {lookupLoading && <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}><CircularProgress /></Box>}
                {lookupError && <Alert severity="error" sx={{ mt: 2 }}>{lookupError}</Alert>}
                {lookupResult && (
                  <Box sx={{ mt: 2, maxHeight: 250, overflow: 'auto' }}>
                    <Alert severity="info">Result found:</Alert>
                    <Button size="small" onClick={() => setShowLookupOutput(v => !v)} sx={{ mt: 1 }}>
                      {showLookupOutput ? 'Hide Output' : 'Show Output'}
                    </Button>
                    <Collapse in={showLookupOutput}>
                      <pre style={{ background: '#f4f4f4', padding: 10, marginTop: 10, borderRadius: 4 }}>{JSON.stringify(lookupResult, null, 2)}</pre>
                    </Collapse>
                  </Box>
                )}
                {lookupResults.length > 0 && (
                  <Box sx={{ mt: 2, maxHeight: 250, overflow: 'auto' }}>
                    <Alert severity="info">Results for this URL:</Alert>
                    <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 200 }}>
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>URL</TableCell>
                            <TableCell>Validation</TableCell>
                            <TableCell>Model Output</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {lookupResults.map(r => (
                            <TableRow key={r.id}>
                              <TableCell>{r.id}</TableCell>
                              <TableCell sx={{ wordBreak: 'break-all' }}>{r.url}</TableCell>
                              <TableCell>{String(r.validation)}</TableCell>
                              <TableCell>
                                <Button size="small" onClick={() => handleToggleLookupRow(r.id)} sx={{ mb: 1 }}>
                                  {openLookupRows[r.id] ? 'Hide Output' : 'Show Output'}
                                </Button>
                                <Collapse in={!!openLookupRows[r.id] ?? true}>
                                  <pre style={{ maxWidth: 300, overflowX: 'auto', margin: 0 }}>{JSON.stringify(r.model_output, null, 2)}</pre>
                                </Collapse>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </AccordionDetails>
        </Accordion>

        <Card elevation={4} sx={{ mb: 2, mt: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
              <Button variant="contained" color="error" onClick={handleDeleteAllResults} disabled={allLoading || allResults.length === 0}>
                Delete All Results
              </Button>
              <Button variant="outlined" onClick={() => setShowIdCol(v => !v)}>
                {showIdCol ? 'Hide ID Column' : 'Show ID Column'}
              </Button>
              <Button variant="outlined" onClick={() => setShowPromptType(v => !v)}>
                {showPromptType ? 'Hide Prompt Type' : 'Show Prompt Type'}
              </Button>
            </Box>
            {allError && <Alert severity="error" sx={{ mt: 2 }}>{allError}</Alert>}
            <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 300 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {showIdCol && <TableCell>ID</TableCell>}
                    <TableCell>Company</TableCell>
                    <TableCell>URL</TableCell>
                    <TableCell>Event Type(s)</TableCell>
                    <TableCell>Significance</TableCell>
                    {showPromptType && <TableCell>Prompt Type</TableCell>}
                    <TableCell>Delete</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allResults.map(r => {
                    const { types, relevant } = getEventSummary(r.model_output);
                    return (
                      <TableRow key={r.id}>
                        {showIdCol && <TableCell>{r.id}</TableCell>}
                        <TableCell>{r.company || ''}</TableCell>
                        <TableCell sx={{ wordBreak: 'break-all' }}>{r.url}</TableCell>
                        <TableCell>{types}</TableCell>
                        <TableCell>{relevant}</TableCell>
                        {showPromptType && <TableCell>{r.template || 'Unknown'}</TableCell>}
                        <TableCell>
                          <Button size="small" color="error" variant="outlined" onClick={() => handleDeleteResult(r.id)}>
                            Delete
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Container>
    </ThemeProvider>
  );
}

export default App;
