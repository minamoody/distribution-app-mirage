<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Company Portal</title>
  
  <!-- ==================== STYLES (CSS) ==================== -->
  <style>
    /* Reset & General Styles */
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    body {
      background-color: #f4f7f6;
      color: #333;
      line-height: 1.6;
    }

    /* Navigation */
    header {
      background: #1e293b;
      color: #fff;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    header h1 {
      font-size: 1.5rem;
    }
    nav a {
      color: #cbd5e1;
      text-decoration: none;
      margin-left: 1.5rem;
      font-weight: 500;
    }
    nav a:hover {
      color: #fff;
    }

    /* Hero Section */
    .hero {
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: white;
      text-align: center;
      padding: 4rem 1rem;
    }
    .hero h2 {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
    }
    .hero p {
      font-size: 1.2rem;
      margin-bottom: 1.5rem;
    }
    .hero button {
      background-color: #f97316;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      border-radius: 6px;
      cursor: pointer;
    }
    .hero button:hover {
      background-color: #ea580c;
    }

    /* Main Container & Cards */
    .container {
      max-width: 1000px;
      margin: 2rem auto;
      padding: 0 1rem;
    }
    .services {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-top: 1rem;
    }
    .card {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card h3 {
      color: #1e293b;
      margin-bottom: 0.5rem;
    }

    /* Contact Form Section */
    .contact-section {
      background: white;
      padding: 2rem;
      border-radius: 8px;
      margin-top: 2rem;
    }
    .contact-section form {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      max-width: 500px;
    }
    .contact-section input, .contact-section textarea {
      padding: 0.75rem;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
    .contact-section button {
      background: #1e293b;
      color: white;
      border: none;
      padding: 0.75rem;
      border-radius: 4px;
      cursor: pointer;
    }

    /* Footer */
    footer {
      text-align: center;
      padding: 1.5rem;
      background: #e2e8f0;
      margin-top: 3rem;
      color: #64748b;
    }
  </style>
</head>
<body>

  <!-- Navigation -->
  <header>
    <h1>My Company</h1>
    <nav>
      <a href="#services">Services</a>
      <a href="#contact">Contact</a>
    </nav>
  </header>

  <!-- Hero Section -->
  <section class="hero">
    <h2>Welcome to Our Company</h2>
    <p>High-quality solutions tailored for your business needs.</p>
    <button onclick="scrollToContact()">Get Started</button>
  </section>

  <!-- Main Content -->
  <main class="container">
    <section id="services">
      <h2>Our Services</h2>
      <div class="services">
        <div class="card">
          <h3>Consulting</h3>
          <p>Expert business and strategy guidance to help you scale rapidly.</p>
        </div>
        <div class="card">
          <h3>E-Commerce</h3>
          <p>Seamless online shopping and automated product fulfillment.</p>
        </div>
        <div class="card">
          <h3>Support</h3>
          <p>24/7 client care to ensure operations run smoothly.</p>
        </div>
      </div>
    </section>

    <!-- Contact Form -->
    <section id="contact" class="contact-section">
      <h2>Contact Us</h2>
      <form id="companyForm">
        <input type="text" id="name" placeholder="Your Name" required>
        <input type="email" id="email" placeholder="Your Email" required>
        <textarea id="message" rows="4" placeholder="Your Message" required></textarea>
        <button type="Here is a complete, fully functional **Company App** packed into a **single self-contained `index.html` file**. 

It uses **React 18** and **Tailwind CSS** (loaded via CDN), so you don't need `npm`, build tools, or terminal setup. Just copy the code, save it as `index.html`, and double-click to open it in any web browser.

---

### `index.html` (Single-File App)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NexusCorp | Modern Company Portal</title>
  <!-- Tailwind CSS CDN -->
  <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
  <!-- React & ReactDOM CDN -->
  <script crossorigin src="[https://unpkg.com/react@18/umd/react.development.js](https://unpkg.com/react@18/umd/react.development.js)"></script>
  <script crossorigin src="[https://unpkg.com/react-dom@18/umd/react-dom.development.js](https://unpkg.com/react-dom@18/umd/react-dom.development.js)"></script>
  <!-- Babel for parsing JSX in browser -->
  <script src="[https://unpkg.com/@babel/standalone/babel.min.js](https://unpkg.com/@babel/standalone/babel.min.js)"></script>
</head>
<body class="bg-slate-900 text-slate-100 antialiased min-h-screen">

  <div id="root"></div>

  <script type="text/babel">
    const { useState } = React;

    // --- Inline Icon Components (Zero external icon dependencies) ---
    const IconBriefcase = () => (
      <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2" strokeWidth="2"></rect>
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" strokeWidth="2"></path>
      </svg>
    );

    const IconUsers = () => (
      <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" strokeWidth="2"></path>
        <circle cx="9" cy="7" r="4" strokeWidth="2"></circle>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" strokeWidth="2"></path>
        <path d="M16 3.13a4 4 0 0 1 0 7.75" strokeWidth="2"></path>
      </svg>
    );

    const IconMail = () => (
      <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" strokeWidth="2"></path>
        <polyline points="22,6 12,13 2,6" strokeWidth="2"></polyline>
      </svg>
    );

    const IconCheck = () => (
      <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <polyline points="20 6 9 17 4 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></polyline>
      </svg>
    );

    // --- Main Company App ---
    function App() {
      const [activeTab, setActiveTab] = useState('home');
      const [formSubmitted, setFormSubmitted] = useState(false);
      const [formData, setFormData] = useState({ name: '', email: '', message: '' });

      const handleContactSubmit = (e) => {
        e.preventDefault();
        setFormSubmitted(true);
        setTimeout(() => {
          setFormSubmitted(false);
          setFormData({ name: '', email: '', message: '' });
        }, 3000);
      };

      const services = [
        { title: 'Digital Transformation', desc: 'Modernizing core infrastructure to drive agility and efficiency.' },
        { title: 'Custom Software Development', desc: 'Scalable web and mobile applications tailored to your business needs.' },
        { title: 'Data Analytics & AI', desc: 'Unlocking actionable insights from complex organizational data.' },
      ];

      const team = [
        { name: 'Sarah Jenkins', role: 'Chief Executive Officer', image: '[https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80](https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80)' },
        { name: 'David Chen', role: 'Head of Technology', image: '[https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80](https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80)' },
        { name: 'Elena Rostova', role: 'Lead Product Designer', image: '[https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80](https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80)' },
      ];

      return (
        <div className="flex flex-col min-h-screen">
          {/* Header Navigation */}
          <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
              <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('home')}>
                <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-indigo-500/30">
                  N
                </div>
                <span className="font-bold text-xl tracking-wide text-white">NexusCorp</span>
              </div>
              <nav className="flex space-x-1 sm:space-x-4">
                {['home', 'services', 'team', 'contact'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium capitalize transition-all ${
                      activeTab === tab
                        ? 'bg-slate-800 text-indigo-400 shadow-sm border border-slate-700'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </nav>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 max-w-6xl mx-auto px-6 py-12 w-full">
            
            {/* Home View */}
            {activeTab === 'home' && (
              <section className="space-y-16">
                <div className="text-center max-w-3xl mx-auto space-y-6">
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    Innovative Tech Solutions
                  </span>
                  <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
                    Building next-generation digital products.
                  </h1>
                  <p className="text-slate-400 text-lg leading-relaxed">
                    We empower enterprises and high-growth startups with modern web architecture, cloud technology, and intuitive design.
                  </p>
                  <div className="flex justify-center space-x-4 pt-4">
                    <button
                      onClick={() => setActiveTab('contact')}
                      className="px-6 py-3 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-500 transition shadow-lg shadow-indigo-600/30"
                    >
                      Get Started
                    </button>
                    <button
                      onClick={() => setActiveTab('services')}
                      className="px-6 py-3 rounded-xl bg-slate-800 text-slate-200 font-medium hover:bg-slate-700 border border-slate-700 transition"
                    >
                      View Services
                    </button>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-8 border-t border-slate-800">
                  {[
                    { label: 'Active Clients', val: '150+' },
                    { label: 'Projects Completed', val: '450+' },
                    { label: 'Team Experts', val: '35' },
                    { label: 'Client Retention', val: '99%' },
                  ].map((stat, idx) => (
                    <div key={idx} className="bg-slate-800/40 border border-slate-800 p-6 rounded-2xl text-center">
                      <div className="text-3xl font-bold text-indigo-400 mb-1">{stat.val}</div>
                      <div className="text-xs text-slate-400 uppercase tracking-wider">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Services View */}
            {activeTab === 'services' && (
              <section className="space-y-8">
                <div>
                  <h2 className="text-3xl font-bold text-white mb-2">Our Services</h2>
                  <p className="text-slate-400">Tailored solutions designed to scale with your business.</p>
                </div>
                <div className="grid md:grid-cols-3 gap-6">
                  {services.map((svc, idx) => (
                    <div key={idx} className="bg-slate-800/50 border border-slate-800 p-6 rounded-2xl hover:border-slate-700 transition">
                      <div className="p-3 bg-indigo-500/10 rounded-xl w-fit mb-4">
                        <IconBriefcase/>
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-2">{svc.title}</h3>
                      <p className="text-slate-400 text-sm leading-relaxed">{svc.desc}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Team View */}
            {activeTab === 'team' && (
              <section className="space-y-8">
                <div>
                  <h2 className="text-3xl font-bold text-white mb-2">Leadership Team</h2>
                  <p className="text-slate-400">The experienced minds behind our solutions.</p>
                </div>
                <div className="grid md:grid-cols-3 gap-6">
                  {team.map((member, idx) => (
                    <div key={idx} className="bg-slate-800/50 border border-slate-800 p-6 rounded-2xl text-center">
                      <img src={member.image} alt={member.name} className="w-24 h-24 rounded-full mx-auto mb-4 object-cover ring-2 ring-indigo-500/30" />
                      <h3 className="text-lg font-semibold text-white">{member.name}</h3>
                      <p className="text-sm text-indigo-400 mt-1">{member.role}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Contact View */}
            {activeTab === 'contact' && (
              <section className="max-w-xl mx-auto space-y-8">
                <div className="text-center">
                  <h2 className="text-3xl font-bold text-white mb-2">Contact Us</h2>
                  <p className="text-slate-400">Send us a message and our team will get back to you within 24 hours.</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-800 p-8 rounded-2xl">
                  {formSubmitted ? (
                    <div className="flex flex-col items-center justify-center py-8 text-center space-y-3">
                      <div className="p-3 bg-emerald-500/10 rounded-full">
                        <IconCheck/>
                      </div>
                      <h4 className="text-lg font-semibold text-white">Message Sent!</h4>
                      <p className="text-sm text-slate-400">Thank you for reaching out. We will respond shorty.</p>
                    </div>
                  ) : (
                    <form onSubmit={handleContactSubmit} className="space-y-4">
                      <div>
                        <label className="block text-xs font-medium text-slate-300 mb-1 uppercase tracking-wider">Full Name</label>
                        <input
                          type="text"
                          required
                          value={formData.name}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 transition text-sm"
                          placeholder="Jane Doe"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-300 mb-1 uppercase tracking-wider">Work Email</label>
                        <input
                          type="email"
                          required
                          value={formData.email}
                          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 transition text-sm"
                          placeholder="jane@company.com"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-300 mb-1 uppercase tracking-wider">Message</label>
                        <textarea
                          rows="4"
                          required
                          value={formData.message}
                          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 transition text-sm"
                          placeholder="Tell us about your project..."
                        ></textarea>
                      </div>
                      <button
                        type="submit"
                        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition shadow-lg shadow-indigo-600/30 text-sm"
                      >
                        Send Message
                      </button>
                    </form>
                  )}
                </div>
              </section>
            )}

          </main>

          {/* Footer */}
          <footer className="border-t border-slate-800 py-8 bg-slate-900/50">
            <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row justify-between items-center text-sm text-slate-500 space-y-4 sm:space-y-0">
              <p>&copy; {new Date().getFullYear()} NexusCorp Technologies. All rights reserved.</p>
              <div className="flex space-x-6">
                <a href="#" className="hover:text-slate-300 transition">Privacy</a>
                <a href="#" className="hover:text-slate-300 transition">Terms</a>
                <a href="#" className="hover:text-slate-300 transition">Security</a>
              </div>
            </div>
          </footer>
        </div>
      );
    }

    // Render the React app
    ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
  </script>
</body>
</html>
