import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ReferenceLine
} from 'recharts';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import axios from 'axios';
import './App.css';

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Main App Component
function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    prices: [],
    events: [],
    changePoints: null,
    impact: [],
    stats: null,
    volatility: null
  });
  const [filters, setFilters] = useState({
    startDate: null,
    endDate: null,
    eventType: 'all',
    severity: 'all',
    selectedEvent: null
  });
  const [selectedTab, setSelectedTab] = useState(0);

  // Fetch all data on component mount
  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [
        pricesRes,
        eventsRes,
        changePointsRes,
        impactRes,
        statsRes,
        volatilityRes
      ] = await Promise.all([
        axios.get(`${API_BASE_URL}/prices`),
        axios.get(`${API_BASE_URL}/events`),
        axios.get(`${API_BASE_URL}/change-points`),
        axios.get(`${API_BASE_URL}/impact`),
        axios.get(`${API_BASE_URL}/stats`),
        axios.get(`${API_BASE_URL}/volatility`)
      ]);

      setData({
        prices: pricesRes.data.data || [],
        events: eventsRes.data.data || [],
        changePoints: changePointsRes.data.data || null,
        impact: impactRes.data.data || [],
        stats: statsRes.data.data || null,
        volatility: volatilityRes.data.data || null
      });
    } catch (err) {
      setError('Failed to fetch data. Please make sure the backend server is running.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter events based on current filters
  const filteredEvents = data.events.filter(event => {
    const eventDate = new Date(event.event_date);
    const matchesType = filters.eventType === 'all' || event.event_type === filters.eventType;
    const matchesSeverity = filters.severity === 'all' || event.severity === filters.severity;
    const matchesStartDate = !filters.startDate || eventDate >= filters.startDate;
    const matchesEndDate = !filters.endDate || eventDate <= filters.endDate;
    
    return matchesType && matchesSeverity && matchesStartDate && matchesEndDate;
  });

  // Prepare data for main price chart
  const prepareChartData = () => {
    if (!data.prices.length) return [];
    
    let chartData = data.prices.map(price => ({
      date: new Date(price.date),
      price: price.price,
      events: []
    }));

    // Add event markers
    filteredEvents.forEach(event => {
      const eventDate = new Date(event.event_date);
      const dataPoint = chartData.find(d => 
        d.date.getDate() === eventDate.getDate() &&
        d.date.getMonth() === eventDate.getMonth() &&
        d.date.getFullYear() === eventDate.getFullYear()
      );
      
      if (dataPoint) {
        dataPoint.events.push(event);
      }
    });

    // Add change points
    if (data.changePoints && data.changePoints.type === 'single') {
      const cpDate = new Date(data.changePoints.mode_date);
      chartData.forEach(d => {
        if (d.date.getTime() === cpDate.getTime()) {
          d.changePoint = true;
        }
      });
    }

    return chartData;
  };

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  // Handle event selection
  const handleEventSelect = async (event) => {
    setFilters(prev => ({ ...prev, selectedEvent: event }));
    
    try {
      const response = await axios.get(
        `${API_BASE_URL}/event-impact/${event.event_date}?window_days=60`
      );
      // You can add logic to display event-specific data here
    } catch (err) {
      console.error('Error fetching event impact:', err);
    }
  };

  // Render loading state
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
        <Typography variant="h6" ml={2}>Loading dashboard data...</Typography>
      </Box>
    );
  }

  // Render error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchAllData}>
          Retry
        </Button>
      </Container>
    );
  }

  const chartData = prepareChartData();

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Brent Oil Price Analysis Dashboard
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Interactive visualization of Brent oil prices, change points, and historical events
            </Typography>
          </Box>
          {data.stats && (
            <Box textAlign="right">
              <Typography variant="body2">
                Data Range: {data.stats.date_range.start} to {data.stats.date_range.end}
              </Typography>
              <Typography variant="body2">
                {data.stats.total_observations.toLocaleString()} price observations
              </Typography>
              <Typography variant="body2">
                {data.stats.total_events?.toLocaleString() || 0} historical events
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={filters.startDate?.toISOString().split('T')[0] || ''}
              onChange={(e) => handleFilterChange('startDate', e.target.value ? new Date(e.target.value) : null)}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="End Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={filters.endDate?.toISOString().split('T')[0] || ''}
              onChange={(e) => handleFilterChange('endDate', e.target.value ? new Date(e.target.value) : null)}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Event Type</InputLabel>
              <Select
                value={filters.eventType}
                label="Event Type"
                onChange={(e) => handleFilterChange('eventType', e.target.value)}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="Geopolitical/Sanctions">Geopolitical/Sanctions</MenuItem>
                <MenuItem value="OPEC Decision">OPEC Decision</MenuItem>
                <MenuItem value="Geopolitical/Conflict">Geopolitical/Conflict</MenuItem>
                <MenuItem value="Economic/Sanctions">Economic/Sanctions</MenuItem>
                <MenuItem value="Government Policy">Government Policy</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select
                value={filters.severity}
                label="Severity"
                onChange={(e) => handleFilterChange('severity', e.target.value)}
              >
                <MenuItem value="all">All Severities</MenuItem>
                <MenuItem value="Very High">Very High</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Main Content Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Price Analysis" />
          <Tab label="Events & Impact" />
          <Tab label="Change Points" />
          <Tab label="Volatility" />
          <Tab label="Statistics" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          {/* Main Price Chart */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Brent Oil Price History with Events
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date"
                    tickFormatter={(date) => new Date(date).toLocaleDateString()}
                  />
                  <YAxis 
                    label={{ value: 'Price (USD)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip 
                    formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
                    labelFormatter={(label) => new Date(label).toLocaleDateString()}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#2E86AB" 
                    strokeWidth={2}
                    dot={false}
                    name="Brent Price"
                  />
                  {data.changePoints && chartData.map((point, index) => (
                    point.changePoint && (
                      <ReferenceLine
                        key={index}
                        x={point.date}
                        stroke="#A23B72"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        label={{ value: 'Change Point', position: 'top' }}
                      />
                    )
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Event List */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: 400, overflow: 'auto' }}>
              <Typography variant="h6" gutterBottom>
                Historical Events ({filteredEvents.length})
              </Typography>
              {filteredEvents.map((event, index) => (
                <Card 
                  key={index} 
                  sx={{ mb: 1, cursor: 'pointer', 
                    backgroundColor: filters.selectedEvent?.event_name === event.event_name ? '#f0f0f0' : 'white' 
                  }}
                  onClick={() => handleEventSelect(event)}
                >
                  <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {new Date(event.event_date).toLocaleDateString()}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {event.event_name}
                        </Typography>
                      </Box>
                      <Chip 
                        label={event.severity} 
                        size="small"
                        color={event.severity === 'Very High' ? 'error' : 
                               event.severity === 'High' ? 'warning' : 'default'}
                      />
                    </Box>
                    <Typography variant="caption" color="textSecondary">
                      {event.event_type}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Paper>
          </Grid>

          {/* Key Metrics */}
          <Grid item xs={12} md={8}>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    ${data.stats?.price_stats?.mean?.toFixed(2) || '0.00'}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Average Price
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="secondary">
                    {data.volatility?.annualized_volatility?.toFixed(2) || '0.00'}%
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Annualized Volatility
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {data.impact[0]?.percent_change?.toFixed(2) || '0.00'}%
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Last Change Point Impact
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {filteredEvents.length}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Filtered Events
                  </Typography>
                </Paper>
              </Grid>

              {/* Impact Chart */}
              <Grid item xs={12}>
                <Paper sx={{ p: 2, mt: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Impact Analysis
                  </Typography>
                  {data.impact.length > 0 && (
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={data.impact}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="closest_event" />
                        <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft' }} />
                        <Tooltip formatter={(value) => [`${value.toFixed(2)}%`, 'Change']} />
                        <Bar dataKey="percent_change" fill="#8884d8" name="Price Change %" />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </Paper>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      )}

      {selectedTab === 1 && (
        <Grid container spacing={3}>
          {/* Events by Type */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Events by Type
              </Typography>
              {data.stats?.events_by_type && (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={Object.entries(data.stats.events_by_type).map(([type, count]) => ({ type, count }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#82ca9d" name="Event Count" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Paper>
          </Grid>

          {/* Events by Severity */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Events by Severity
              </Typography>
              {data.stats?.events_by_severity && (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={Object.entries(data.stats.events_by_severity).map(([severity, count]) => ({ severity, count }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="severity" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" name="Event Count" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}

      {selectedTab === 2 && data.changePoints && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Change Point Analysis
          </Typography>
          {data.changePoints.type === 'single' && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Detected Change Point
                  </Typography>
                  <Typography variant="body2">
                    <strong>Date:</strong> {new Date(data.changePoints.mode_date).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2">
                    <strong>95% HDI:</strong> {new Date(data.changePoints.hdi_95_dates[0]).toLocaleDateString()} to {new Date(data.changePoints.hdi_95_dates[1]).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Mean Index:</strong> {data.changePoints.mean}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Median Index:</strong> {data.changePoints.median}
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Impact Summary
                  </Typography>
                  {data.impact.map((impact, index) => (
                    <Box key={index} mb={2}>
                      <Typography variant="body2">
                        <strong>Before Change:</strong> {impact.before_mean?.toFixed(6)}
                      </Typography>
                      <Typography variant="body2">
                        <strong>After Change:</strong> {impact.after_mean?.toFixed(6)}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Change:</strong> {impact.percent_change?.toFixed(2)}%
                      </Typography>
                      <Typography variant="body2">
                        <strong>Closest Event:</strong> {impact.closest_event}
                      </Typography>
                    </Box>
                  ))}
                </Card>
              </Grid>
            </Grid>
          )}
        </Paper>
      )}

      {selectedTab === 3 && data.volatility && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Volatility Metrics
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(data.volatility).map(([key, value]) => (
                  <Grid item xs={6} key={key}>
                    <Card sx={{ p: 1 }}>
                      <Typography variant="caption" color="textSecondary">
                        {key.replace(/_/g, ' ').toUpperCase()}
                      </Typography>
                      <Typography variant="h6">
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </Typography>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}

      {selectedTab === 4 && data.stats && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Dataset Statistics
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Price Statistics
                </Typography>
                {Object.entries(data.stats.price_stats).map(([key, value]) => (
                  <Typography key={key} variant="body2">
                    <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> ${typeof value === 'number' ? value.toFixed(2) : value}
                  </Typography>
                ))}
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Event Statistics
                </Typography>
                <Typography variant="body2">
                  <strong>Total Events:</strong> {data.stats.total_events || 0}
                </Typography>
                <Typography variant="body2">
                  <strong>Date Range:</strong> {data.stats.date_range.start} to {data.stats.date_range.end}
                </Typography>
                <Typography variant="body2">
                  <strong>Total Price Observations:</strong> {data.stats.total_observations.toLocaleString()}
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Footer */}
      <Box mt={4} pt={2} borderTop={1} borderColor="divider">
        <Typography variant="body2" color="textSecondary" align="center">
          Brent Oil Price Analysis Dashboard • Birhan Energies • Data from 1987-2022
        </Typography>
      </Box>
    </Container>
  );
}

export default App;