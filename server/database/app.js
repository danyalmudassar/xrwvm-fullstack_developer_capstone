const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors')
const app = express()
const port = 3030;

app.use(cors())
app.use(require('body-parser').urlencoded({ extended: false }));

// Read data files
const reviews_data = JSON.parse(fs.readFileSync("reviews.json", 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync("dealerships.json", 'utf8'));

// MongoDB Connection
// Note: 'mongo_db' should resolve to your MongoDB service name in docker-compose.yml
mongoose.connect("mongodb://mongo_db:27017/",{'dbName':'dealershipsDB'});

// Mongoose Models
const Reviews = require('./review');
const Dealerships = require('./dealership');

// Initial Data Loading (Idempotent operation to ensure data is present)
try {
  Reviews.deleteMany({}).then(()=>{
    Reviews.insertMany(reviews_data['reviews']);
  });
  Dealerships.deleteMany({}).then(()=>{
    Dealerships.insertMany(dealerships_data['dealerships']);
  });
  
} catch (error) {
  // Catch block logic here is slightly misplaced as it runs before routes are defined
  // console.error("Error loading initial data:", error);
}

// Express route to home
app.get('/', async (req, res) => {
    res.send("Welcome to the Mongoose API")
});

// Express route to fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({dealership: req.params.id});
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// ************************************************************
// IMPLEMENTATION START
// ************************************************************

// Express route to fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    // Find all documents in the Dealerships collection
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    console.error("Error fetching all dealers:", error);
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

// Express route to fetch Dealers by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const stateName = req.params.state;
    // Find documents where the 'state' field matches the URL parameter
    const documents = await Dealerships.find({ state: stateName }); 
    res.json(documents);
  } catch (error) {
    console.error(`Error fetching dealers by state ${req.params.state}:`, error);
    res.status(500).json({ error: 'Error fetching dealerships by state' });
  }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const dealerId = req.params.id;
    // Find a single document where the 'id' field matches the URL parameter
    // Assuming the 'id' in your schema is the unique identifier you want to query by.
    const document = await Dealerships.findOne({ id: dealerId }); 
    
    if (document) {
      res.json(document);
    } else {
      res.status(404).json({ error: 'Dealer not found' });
    }
  } catch (error) {
    console.error(`Error fetching dealer by ID ${req.params.id}:`, error);
    res.status(500).json({ error: 'Error fetching dealer details' });
  }
});

// ************************************************************
// IMPLEMENTATION END
// ************************************************************

//Express route to insert review (already implemented, but using raw body parser is tricky)
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  // Note: Using req.body as a buffer requires parsing it manually
  let data;
  try {
    data = JSON.parse(req.body.toString());
  } catch (parseError) {
    return res.status(400).json({ error: 'Invalid JSON format' });
  }

  // Find the max ID to assign a new ID (less robust than using MongoDB's _id, but follows existing logic)
  const documents = await Reviews.find().sort( { id: -1 } ).limit(1);
  let new_id = documents.length > 0 ? documents[0]['id'] + 1 : 1;

  const review = new Reviews({
        "id": new_id,
        "name": data['name'],
        "dealership": data['dealership'],
        "review": data['review'],
        "purchase": data['purchase'],
        "purchase_date": data['purchase_date'],
        "car_make": data['car_make'],
        "car_model": data['car_model'],
        "car_year": data['car_year'],
    });

  try {
    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.error("Error inserting review:", error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});