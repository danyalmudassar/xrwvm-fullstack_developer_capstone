import LoginPanel from "./components/Login/Login"
import Home from "./components/Home/Home";
import About from "./components/About/About";
import Contact from "./components/Contact/Contact";
import Header from "./components/Header/Header";
import { Routes, Route } from "react-router-dom";
// 1. IMPORT THE REGISTER COMPONENT
import Register from "./components/Register/Register";

function App() {
  return (
    <div>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/login" element={<LoginPanel />} />
        {/* 2. ADD THE NEW REGISTRATION ROUTE */}
        <Route path="/register" element={<Register />} /> 
      </Routes>
    </div>
  );
}
export default App;