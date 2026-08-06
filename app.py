<!DOCTYPE html>
<html lang="en" dir="ltr" id="appRoot" class="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Global Enterprise Distribution & Supply Chain Hub</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eff6ff',
              100: '#dbeafe',
              500: '#3b82f6',
              600: '#2563eb',
              700: '#1d4ed8',
              900: '#1e3a8a',
            }
          }
        }
      }
    }
  </script>

  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  
  <style>
    /* Custom Scrollbar Styling */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 4px;
    }
    .dark ::-webkit-scrollbar-thumb {
      background: #475569;
    }
  </style>
</head>
<body class="bg-gray-100 dark:bg-gray-950 text-gray-800 dark:text-gray-100 font-sans transition-colors duration-300 min-h-screen flex flex-col">

  <!-- TOP NAVIGATION / HEADER -->
  <header class="sticky top-0 z-30 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 px-4 lg:px-8 py-3 transition-colors">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      
      <!-- Brand Logo & Title -->
      <div class="flex items-center space-x-3 rtl:space-x-reverse">
        <div class="p-2.5 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl text-white font-black text-2xl shadow-lg shadow-blue-500/30 flex items-center justify-center w-11 h-11">
          🌐
        </div>
        <div>
          <div class="flex items-center space-x-2 rtl:space-x-reverse">
            <h1 id="appTitle" class="text-xl font-bold tracking-tight text-gray-900 dark:text-white">Global Distribution Command</h1>
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300">v4.0 Ultra</span>
          </div>
          <p id="appSubtitle" class="text-xs text-gray-500 dark:text-gray-400">Real-time supply chain analytics, fleet telemetry, and inventory management</p>
        </div>
      </div>

      <!-- Top Bar Global Actions -->
      <div class="flex flex-wrap items-center gap-2 sm:gap-3 rtl:space-x-reverse">
        
        <!-- Dark / Light Theme Toggle -->
        <button onclick="toggleTheme()" class="p-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg text-sm font-semibold transition flex items-center gap-1.5" title="Toggle UI Theme">
          <span id="themeIcon">🌙</span>
          <span id="themeLabel" class="hidden md:inline text-xs">Dark Mode</span>
        </button>

        <!-- Role Access Selector -->
        <div class="relative">
          <select id="roleSelect" onchange="switchRole(this.value)" class="bg-gray-100 dark:bg-gray-800 dark:text-gray-200 text-gray-700 text-xs sm:text-sm font-semibold py-2 px-3 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="admin">⚙️ Admin View</option>
            <option value="manager">📊 Logistics Manager</option>
            <option value="operator">🚚 Dispatch Operator</option>
          </select>
        </div>

        <!-- Language Switcher -->
        <div class="relative">
          <select id="langSelect" onchange="switchLanguage(this.value)" class="bg-gray-100 dark:bg-gray-800 dark:text-gray-200 text-gray-700 text-xs sm:text-sm font-semibold py-2 px-3 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="en" selected>🌐 English</option>
            <option value="ar">🌐 العربية</option>
          </select>
        </div>

        <!-- Currency Switcher -->
        <div class="relative">
          <select id="currencySelect" onchange="switchCurrency(this.value)" class="bg-gray-100 dark:bg-gray-800 dark:text-gray-200 text-gray-700 text-xs sm:text-sm font-semibold py-2 px-3 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="USD">USD ($)</option>
            <option value="EGP">EGP (E£)</option>
            <option value="EUR">EUR (€)</option>
          </select>
        </div>

        <!-- Create New Order/Shipment Button (Admin / Manager Only) -->
        <button id="btnNewShipment" onclick="openModal('shipmentModal')" class="admin-only manager-only bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-semibold py-2 px-4 rounded-lg transition shadow-md shadow-blue-500/20 flex items-center gap-1">
          <span>+</span> <span id="lblBtnNew">New Shipment</span>
        </button>

        <!-- Export Data Button (Admin / Manager Only) -->
        <button id="btnExport" onclick="exportToCSV()" class="admin-only manager-only bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm font-semibold py-2 px-4 rounded-lg transition shadow-md shadow-emerald-500/20 flex items-center gap-1">
          <span>📥</span> <span id="lblBtnExport">Export CSV</span>
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN DASHBOARD CONTENT CONTAINER -->
  <main class="max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6 flex-grow">

    <!-- SYSTEM ALERTS BANNER -->
    <div id="systemAlertBanner" class="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-l-4 border-amber-500 p-4 rounded-r-xl flex items-center justify-between dark:text-amber-200 text-amber-900">
      <div class="flex items-center space-x-3 rtl:space-x-reverse">
        <span class="text-amber-500 text-xl">⚠️</span>
        <div>
          <p class="font-bold text-sm" id="alertTitle">Regional Weather Advisory</p>
          <p class="text-xs text-amber-700 dark:text-amber-300" id="alertBody">Port delays reported in Alexandria Terminal 2. Estimated lead time offset: +4 hours.</p>
        </div>
      </div>
      <button onclick="document.getElementById('systemAlertBanner').remove()" class="text-amber-500 hover:text-amber-700 text-sm font-bold">✕</button>
    </div>

    <!-- ADVANCED FILTER & SEARCH CONTROL RIBBON -->
    <section class="bg-white dark:bg-gray-900 p-4 sm:p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm space-y-4">
      <div class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        
        <!-- Search Input -->
        <div class="flex-1">
          <label id="lblSearch" class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1.5">Live Shipment Search</label>
          <div class="relative">
            <input type="text" id="searchInput" oninput="applyFilters()" placeholder="Search by tracking ID, origin, destination, or carrier..." class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 text-sm rounded-xl p-2.5 pl-9 rtl:pr-9 rtl:pl-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            <span class="absolute left-3 rtl:right-3 rtl:left-auto top-3 text-gray-400">🔍</span>
          </div>
        </div>

        <!-- Filter Dropdown Group -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          
          <!-- Category Filter -->
          <div>
            <label id="lblCategory" class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1.5">Category</label>
            <select id="categoryFilter" onchange="applyFilters()" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 text-xs sm:text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500">
              <option value="all">All Categories</option>
              <option value="Electronics">Electronics</option>
              <option value="Pharmaceuticals">Pharmaceuticals</option>
              <option value="Heavy Machinery">Heavy Machinery</option>
              <option value="Consumer Goods">Consumer Goods</option>
            </select>
          </div>

          <!-- Status Filter -->
          <div>
            <label id="lblStatus" class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1.5">Shipment Status</label>
            <select id="statusFilter" onchange="applyFilters()" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 text-xs sm:text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500">
              <option value="all">All Statuses</option>
              <option value="In Transit">In Transit</option>
              <option value="Delivered">Delivered</option>
              <option value="Customs Hold">Customs Hold</option>
              <option value="Pending Dispatch">Pending Dispatch</option>
            </select>
          </div>

          <!-- Priority Filter -->
          <div>
            <label id="lblPriority" class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1.5">Priority Level</label>
            <select id="priorityFilter" onchange="applyFilters()" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 text-xs sm:text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500">
              <option value="all">All Priorities</option>
              <option value="Express">🔴 Express</option>
              <option value="Standard">🟡 Standard</option>
              <option value="Economy">🟢 Economy</option>
            </select>
          </div>

          <!-- Timeframe Selector -->
          <div>
            <label id="lblTimeframe" class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1.5">Timeframe</label>
            <select id="timeframeFilter" onchange="applyFilters()" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 text-xs sm:text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500">
              <option value="7d">Last 7 Days</option>
              <option value="30d" selected>Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Full Year</option>
            </select>
          </div>

        </div>
      </div>
    </section>

    <!-- METRICS & KPI DISPLAY CARDS -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <div class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm relative overflow-hidden group">
        <div class="flex justify-between items-start">
          <div>
            <p id="kpi1Title" class="text-xs font-bold uppercase text-gray-400 tracking-wider">Total Active Fleet</p>
            <h3 id="kpi1Val" class="text-3xl font-black text-gray-900 dark:text-white mt-1">1,420</h3>
          </div>
          <span class="p-3 bg-blue-50 dark:bg-blue-900/40 text-blue-600 rounded-xl text-xl">🚚</span>
        </div>
        <div class="mt-3 flex items-center text-xs font-semibold text-emerald-600">
          <span>↑ 94.2% Fleet Utilization</span>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm relative overflow-hidden group">
        <div class="flex justify-between items-start">
          <div>
            <p id="kpi2Title" class="text-xs font-bold uppercase text-gray-400 tracking-wider">On-Time Delivery Rate</p>
            <h3 id="kpi2Val" class="text-3xl font-black text-gray-900 dark:text-white mt-1">98.4%</h3>
          </div>
          <span class="p-3 bg-emerald-50 dark:bg-emerald-900/40 text-emerald-600 rounded-xl text-xl">⏱️</span>
        </div>
        <div class="mt-3 flex items-center text-xs font-semibold text-emerald-600">
          <span>↑ +1.8% vs last quarter</span>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm relative overflow-hidden group">
        <div class="flex justify-between items-start">
          <div>
            <p id="kpi3Title" class="text-xs font-bold uppercase text-gray-400 tracking-wider">Average Dispatch Cost</p>
            <h3 id="kpi3Val" class="text-3xl font-black text-gray-900 dark:text-white mt-1">$450.00</h3>
          </div>
          <span class="p-3 bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 rounded-xl text-xl">💰</span>
        </div>
        <div class="mt-3 flex items-center text-xs font-semibold text-emerald-600">
          <span>↓ 3.1% Cost Optimization</span>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm relative overflow-hidden group">
        <div class="flex justify-between items-start">
          <div>
            <p id="kpi4Title" class="text-xs font-bold uppercase text-gray-400 tracking-wider">Warehouse Storage Load</p>
            <h3 id="kpi4Val" class="text-3xl font-black text-gray-900 dark:text-white mt-1">82.5%</h3>
          </div>
          <span class="p-3 bg-amber-50 dark:bg-amber-900/40 text-amber-600 rounded-xl text-xl">🏭</span>
        </div>
        <div class="mt-3 flex items-center text-xs font-semibold text-amber-600">
          <span>⚠️ High Load in Hub 3</span>
        </div>
      </div>

    </section>

    <!-- ANALYTICS VISUALIZATION SECTION (CHARTS) -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Line Chart: Throughput -->
      <div class="lg:col-span-2 bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 id="chart1Title" class="text-base font-bold text-gray-900 dark:text-white">Shipment Delivery Performance</h2>
            <p id="chart1Sub" class="text-xs text-gray-400">Monthly dispatch volume vs target efficiency SLA</p>
          </div>
          <span class="text-xs font-semibold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 px-3 py-1 rounded-lg">Real-Time Sync</span>
        </div>
        <div class="h-72 w-full">
          <canvas id="throughputChart"></canvas>
        </div>
      </div>

      <!-- Doughnut Chart: Regional Distribution -->
      <div class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 id="chart2Title" class="text-base font-bold text-gray-900 dark:text-white">Regional Hub Volumes</h2>
            <p id="chart2Sub" class="text-xs text-gray-400">Distribution breakdown across major hubs</p>
          </div>
        </div>
        <div class="h-72 w-full relative flex items-center justify-center">
          <canvas id="regionalChart"></canvas>
        </div>
      </div>

    </section>

    <!-- DYNAMIC SHIPMENT DATA TABLE SECTION -->
    <section class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
      
      <!-- Table Header Bar -->
      <div class="p-5 border-b border-gray-200 dark:border-gray-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-3 rtl:space-x-reverse">
            <h2 id="tableHeading" class="text-lg font-bold text-gray-900 dark:text-white">Active Global Shipments</h2>
            <span id="recordCounter" class="bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 text-xs font-bold px-2.5 py-1 rounded-full">5 Records</span>
          </div>
          <p id="tableSubheading" class="text-xs text-gray-400 mt-0.5">Filter, track, manage status, and delete active shipments</p>
        </div>

        <div class="flex items-center space-x-2 rtl:space-x-reverse">
          <span id="userRoleBadge" class="text-xs px-3 py-1.5 rounded-xl bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 font-bold">
            Role: Admin
          </span>
        </div>
      </div>

      <!-- Table Wrapper -->
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left rtl:text-right text-gray-600 dark:text-gray-300">
          <thead class="bg-gray-50 dark:bg-gray-800/60 text-xs uppercase tracking-wider text-gray-400 font-bold border-b border-gray-200 dark:border-gray-800">
            <tr>
              <th scope="col" class="p-4" id="thTrackId">Tracking ID</th>
              <th scope="col" class="p-4" id="thRoute">Origin → Destination</th>
              <th scope="col" class="p-4" id="thCategory">Category</th>
              <th scope="col" class="p-4" id="thPriority">Priority</th>
              <th scope="col" class="p-4" id="thStatus">Status</th>
              <th scope="col" class="p-4" id="thCost">Declared Cost</th>
              <th scope="col" class="p-4 text-right rtl:text-left admin-only manager-only" id="thActions">Actions</th>
            </tr>
          </thead>
          <tbody id="shipmentTableBody" class="divide-y divide-gray-200 dark:divide-gray-800">
            <!-- Table Rows Rendered via JavaScript -->
          </tbody>
        </table>
      </div>

      <!-- Table Footer / Pagination -->
      <div class="p-4 bg-gray-50 dark:bg-gray-800/40 border-t border-gray-200 dark:border-gray-800 flex flex-wrap items-center justify-between gap-4 text-xs font-medium text-gray-500">
        <span id="paginationInfo">Showing 1 to 5 of 5 entries</span>
        <div class="flex items-center space-x-2 rtl:space-x-reverse">
          <button disabled class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-400 cursor-not-allowed">Previous</button>
          <button disabled class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-400 cursor-not-allowed">Next</button>
        </div>
      </div>

    </section>

    <!-- BOTTOM ROW: WAREHOUSE STOCK & LIVE SYSTEM AUDIT LOG -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Warehouse Capacity Monitor -->
      <div class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm space-y-4">
        <div class="flex items-center justify-between">
          <h2 id="whTitle" class="text-base font-bold text-gray-900 dark:text-white">Warehouse Inventory Levels</h2>
          <span class="text-xs text-blue-600 font-bold">4 Major Hubs</span>
        </div>
        <div class="space-y-3">
          
          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span>Cairo Regional Logistics Center (Hub 1)</span>
              <span class="text-blue-600 font-bold">78%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2.5">
              <div class="bg-blue-600 h-2.5 rounded-full" style="width: 78%"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span>Alexandria Maritime Port Storage (Hub 2)</span>
              <span class="text-amber-600 font-bold">92% (High Capacity)</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2.5">
              <div class="bg-amber-500 h-2.5 rounded-full" style="width: 92%"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span>10th of Ramadan Distribution Center (Hub 3)</span>
              <span class="text-emerald-600 font-bold">45%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2.5">
              <div class="bg-emerald-500 h-2.5 rounded-full" style="width: 45%"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span>Upper Egypt Logistics Station (Hub 4)</span>
              <span class="text-blue-600 font-bold">64%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2.5">
              <div class="bg-blue-500 h-2.5 rounded-full" style="width: 64%"></div>
            </div>
          </div>

        </div>
      </div>

      <!-- Live Real-Time System Audit Log -->
      <div class="bg-white dark:bg-gray-900 p-5 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between mb-3">
          <h2 id="logTitle" class="text-base font-bold text-gray-900 dark:text-white">Live System Audit Stream</h2>
          <span class="flex items-center gap-1.5 text-xs text-emerald-500 font-semibold">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span> Live Broadcast
          </span>
        </div>

        <div id="auditLogContainer" class="space-y-2.5 max-h-48 overflow-y-auto pr-1 text-xs">
          <!-- Log Entries dynamically generated -->
        </div>

        <button onclick="clearLogs()" class="mt-3 text-xs font-semibold text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-left rtl:text-right">
          Clear Activity Stream
        </button>
      </div>

    </section>

  </main>

  <!-- MODAL: ADD NEW SHIPMENT (ADMIN / MANAGER) -->
  <div id="shipmentModal" class="fixed inset-0 z-50 hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl max-w-lg w-full p-6 space-y-4 animate-in fade-in zoom-in duration-200">
      <div class="flex justify-between items-center border-b border-gray-200 dark:border-gray-800 pb-3">
        <h3 id="modalTitle" class="text-lg font-bold text-gray-900 dark:text-white">Dispatch New Shipment</h3>
        <button onclick="closeModal('shipmentModal')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 font-bold text-lg">✕</button>
      </div>

      <form id="newShipmentForm" onsubmit="handleCreateShipment(event)" class="space-y-3">
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">Tracking ID</label>
          <input type="text" id="inputTrackId" required placeholder="TRK-99001" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none dark:text-white" />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">Origin City</label>
            <input type="text" id="inputOrigin" required placeholder="Cairo" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none dark:text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">Destination City</label>
            <input type="text" id="inputDestination" required placeholder="Alexandria" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none dark:text-white" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">Category</label>
            <select id="inputCategory" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 dark:text-white">
              <option value="Electronics">Electronics</option>
              <option value="Pharmaceuticals">Pharmaceuticals</option>
              <option value="Heavy Machinery">Heavy Machinery</option>
              <option value="Consumer Goods">Consumer Goods</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">Priority</label>
            <select id="inputPriority" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 dark:text-white">
              <option value="Express">Express</option>
              <option value="Standard">Standard</option>
              <option value="Economy">Economy</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">Initial Status</label>
            <select id="inputStatus" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 dark:text-white">
              <option value="Pending Dispatch">Pending Dispatch</option>
              <option value="In Transit">In Transit</option>
              <option value="Customs Hold">Customs Hold</option>
              <option value="Delivered">Delivered</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">Declared Value ($ USD)</label>
            <input type="number" id="inputCost" required placeholder="12500" class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none dark:text-white" />
          </div>
        </div>

        <div class="flex justify-end space-x-2 rtl:space-x-reverse pt-3">
          <button type="button" onclick="closeModal('shipmentModal')" class="px-4 py-2 text-xs font-semibold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">Cancel</button>
          <button type="submit" class="px-5 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-md shadow-blue-500/20">Submit Order</button>
        </div>
      </form>
    </div>
  </div>

  <!-- FOOTER -->
  <footer class="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-4 px-6 text-center text-xs text-gray-400 transition-colors">
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
      <p>© 2026 Enterprise Distribution System. All Rights Reserved.</p>
      <div class="flex items-center space-x-4 rtl:space-x-reverse">
        <a href="#" class="hover:underline">System Status</a>
        <a href="#" class="hover:underline">Privacy Policy</a>
        <a href="#" class="hover:underline">API Documentation</a>
      </div>
    </div>
  </footer>

  <!-- SCRIPT LOGIC ENGINE -->
  <script>
    // --- GLOBAL DATA STORE ---
    let currentRole = 'admin';
    let currentLang = 'en';
    let currentCurrency = 'USD';
    let currencyRates = { USD: 1, EGP: 48.5, EUR: 0.92 };
    let currencySymbols = { USD: '$', EGP: 'E£', EUR: '€' };

    let shipments = [
      { id: 'TRK-10482', origin: 'Cairo Hub', destination: 'Alexandria Port', category: 'Electronics', priority: 'Express', status: 'In Transit', costUSD: 14500 },
      { id: 'TRK-20911', origin: 'Tanta Depot', destination: 'Giza Hub', category: 'Pharmaceuticals', priority: 'Standard', status: 'Delivered', costUSD: 8200 },
      { id: 'TRK-30194', origin: '10th of Ramadan', destination: 'Suez Customs', category: 'Heavy Machinery', priority: 'Express', status: 'Customs Hold', costUSD: 45000 },
      { id: 'TRK-40812', origin: 'Luxor Station', destination: 'Aswan Terminal', category: 'Consumer Goods', priority: 'Economy', status: 'In Transit', costUSD: 3400 },
      { id: 'TRK-50119', origin: 'Mansoura Depot', destination: 'Cairo Hub', category: 'Electronics', priority: 'Standard', status: 'Pending Dispatch', costUSD: 19800 }
    ];

    let auditLogs = [
      { time: '11:02 AM', text: 'Shipment TRK-30194 flagged for Customs Review at Suez.' },
      { time: '10:45 AM', text: 'User (Admin) updated USD/EGP exchange rate matrix.' },
      { time: '09:30 AM', text: 'Driver assigned to TRK-10482 (Vehicle Fleet #402).' },
      { time: '08:15 AM', text: 'Warehouse Hub 2 reached 92% storage threshold alert.' }
    ];

    // --- TRANSLATION DICTIONARY ---
    const i18n = {
      en: {
        appTitle: "Global Distribution Command",
        appSubtitle: "Real-time supply chain analytics, fleet telemetry, and inventory management",
        btnNew: "New Shipment",
        btnExport: "Export CSV",
        searchLabel: "Live Shipment Search",
        catLabel: "Category",
        statusLabel: "Shipment Status",
        prioLabel: "Priority Level",
        timeLabel: "Timeframe",
        kpi1: "Total Active Fleet",
        kpi2: "On-Time Delivery Rate",
        kpi3: "Average Dispatch Cost",
        kpi4: "Warehouse Storage Load",
        chart1Title: "Shipment Delivery Performance",
        chart1Sub: "Monthly dispatch volume vs target efficiency SLA",
        chart2Title: "Regional Hub Volumes",
        chart2Sub: "Distribution breakdown across major hubs",
        tableHeading: "Active Global Shipments",
        tableSub: "Filter, track, manage status, and delete active shipments",
        thTrackId: "Tracking ID",
        thRoute: "Origin → Destination",
        thCategory: "Category",
        thPriority: "Priority",
        thStatus: "Status",
        thCost: "Declared Cost",
        thActions: "Actions",
        whTitle: "Warehouse Inventory Levels",
        logTitle: "Live System Audit Stream"
      },
      ar: {
        appTitle: "مركز قيادة التوزيع العالمي",
        appSubtitle: "تحليلات سلسلة التوريد في الوقت الفعلي ومراقبة الأسطول والمخزون",
        btnNew: "شحنة جديدة",
        btnExport: "تصدير CSV",
        searchLabel: "البحث المباشر للشحنات",
        catLabel: "التصنيف",
        statusLabel: "حالة الشحنة",
        prioLabel: "مستوى الأولوية",
        timeLabel: "الإطار الزمني",
        kpi1: "إجمالي الأسطول النشط",
        kpi2: "معدل التسليم في الوقت المحدد",
        kpi3: "متوسط تكلفة الإرسال",
        kpi4: "حمل التخزين بالمستودعات",
        chart1Title: "أداء تسليم الشحنات",
        chart1Sub: "حجم الإرسال الشهري مقابل كفاءة اتفاقية مستوى الخدمة",
        chart2Title: "أحجام المراكز الإقليمية",
        chart2Sub: "توزيع الشحنات عبر المراكز الرئيسية",
        tableHeading: "الشحنات العالمية النشطة",
        tableSub: "تصفية وتتبع وإدارة الحالة وحذف الشحنات النشطة",
        thTrackId: "رمز التتبع",
        thRoute: "المصدر ← الوجهة",
        thCategory: "التصنيف",
        thPriority: "الأولوية",
        thStatus: "الحالة",
        thCost: "القيمة المصرح بها",
        thActions: "الإجراءات",
        whTitle: "مستويات المخزون بالمستودعات",
        logTitle: "سجل تدقيق النظام المباشر"
      }
    };

    // --- CHART INITIALIZATIONS ---
    let throughputChartObj, regionalChartObj;

    function initCharts() {
      // Line Chart
      const ctx1 = document.getElementById('throughputChart').getContext('2d');
      throughputChartObj = new Chart(ctx1, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
          datasets: [
            {
              label: 'Dispatched Volume',
              data: [1200, 1400, 1350, 1600, 1550, 1800, 1950],
              borderColor: '#2563eb',
              backgroundColor: 'rgba(37, 99, 235, 0.1)',
              fill: true,
              tension: 0.4
            },
            {
              label: 'Delivered On-Time',
              data: [1150, 1360, 1310, 1580, 1520, 1770, 1910],
              borderColor: '#10b981',
              backgroundColor: 'transparent',
              borderDash: [5, 5],
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          scales: { y: { beginAtZero: false } }
        }
      });

      // Doughnut Chart
      const ctx2 = document.getElementById('regionalChart').getContext('2d');
      regionalChartObj = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: ['Greater Cairo', 'Alexandria Port', 'Delta Hubs', 'Upper Egypt'],
          datasets: [{
            data: [42, 28, 18, 12],
            backgroundColor: ['#2563eb', '#f59e0b', '#10b981', '#8b5cf6']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } }
        }
      });
    }

    // --- THEME ENGINE ---
    function toggleTheme() {
      const html = document.getElementById('appRoot');
      const icon = document.getElementById('themeIcon');
      const label = document.getElementById('themeLabel');
      
      if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        icon.innerText = '🌙';
        label.innerText = 'Dark Mode';
      } else {
        html.classList.add('dark');
        icon.innerText = '☀️';
        label.innerText = 'Light Mode';
      }
    }

    // --- INTERNATIONALIZATION (LANGUAGE) ENGINE ---
    function switchLanguage(lang) {
      currentLang = lang;
      const html = document.getElementById('appRoot');
      html.lang = lang;
      html.dir = lang === 'ar' ? 'rtl' : 'ltr';

      const t = i18n[lang];
      document.getElementById('appTitle').innerText = t.appTitle;
      document.getElementById('appSubtitle').innerText = t.appSubtitle;
      document.getElementById('lblBtnNew').innerText = t.btnNew;
      document.getElementById('lblBtnExport').innerText = t.btnExport;
      document.getElementById('lblSearch').innerText = t.searchLabel;
      document.getElementById('lblCategory').innerText = t.catLabel;
      document.getElementById('lblStatus').innerText = t.statusLabel;
      document.getElementById('lblPriority').innerText = t.prioLabel;
      document.getElementById('lblTimeframe').innerText = t.timeLabel;
      document.getElementById('kpi1Title').innerText = t.kpi1;
      document.getElementById('kpi2Title').innerText = t.kpi2;
      document.getElementById('kpi3Title').innerText = t.kpi3;
      document.getElementById('kpi4Title').innerText = t.kpi4;
      document.getElementById('chart1Title').innerText = t.chart1Title;
      document.getElementById('chart1Sub').innerText = t.chart1Sub;
      document.getElementById('chart2Title').innerText = t.chart2Title;
      document.getElementById('chart2Sub').innerText = t.chart2Sub;
      document.getElementById('tableHeading').innerText = t.tableHeading;
      document.getElementById('tableSubheading').innerText = t.tableSub;
      document.getElementById('thTrackId').innerText = t.thTrackId;
      document.getElementById('thRoute').innerText = t.thRoute;
      document.getElementById('thCategory').innerText = t.thCategory;
      document.getElementById('thPriority').innerText = t.thPriority;
      document.getElementById('thStatus').innerText = t.thStatus;
      document.getElementById('thCost').innerText = t.thCost;
      document.getElementById('thActions').innerText = t.thActions;
      document.getElementById('whTitle').innerText = t.whTitle;
      document.getElementById('logTitle').innerText = t.logTitle;

      renderTable();
    }

    // --- ROLE-BASED ACCESS CONTROL (RBAC) ---
    function switchRole(role) {
      currentRole = role;
      document.getElementById('userRoleBadge').innerText = `Role: ${role.charAt(0).toUpperCase() + role.slice(1)}`;
      
      const adminElems = document.querySelectorAll('.admin-only');
      const managerElems = document.querySelectorAll('.manager-only');

      adminElems.forEach(el => el.style.display = (role === 'admin') ? '' : 'none');
      managerElems.forEach(el => el.style.display = (role === 'admin' || role === 'manager') ? '' : 'none');

      renderTable();
    }

    // --- CURRENCY CONVERTOR ENGINE ---
    function switchCurrency(curr) {
      currentCurrency = curr;
      const rate = currencyRates[curr];
      const symbol = currencySymbols[curr];
      
      // Update KPI Cost
      const baseCost = 450.00;
      document.getElementById('kpi3Val').innerText = `${symbol}${(baseCost * rate).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

      renderTable();
    }

    // --- RENDER TABLE WITH SEARCH & FILTERS ---
    function renderTable(data = shipments) {
      const tbody = document.getElementById('shipmentTableBody');
      tbody.innerHTML = '';

      const rate = currencyRates[currentCurrency];
      const symbol = currencySymbols[currentCurrency];

      data.forEach(item => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50/60 dark:hover:bg-gray-800/40 transition border-b border-gray-100 dark:border-gray-800/50';

        // Badge Status Styling
        let statusBadge = '';
        if (item.status === 'In Transit') statusBadge = '<span class="bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 text-xs font-bold px-2.5 py-1 rounded-full">In Transit</span>';
        else if (item.status === 'Delivered') statusBadge = '<span class="bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 text-xs font-bold px-2.5 py-1 rounded-full">Delivered</span>';
        else if (item.status === 'Customs Hold') statusBadge = '<span class="bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 text-xs font-bold px-2.5 py-1 rounded-full">Customs Hold</span>';
        else statusBadge = '<span class="bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 text-xs font-bold px-2.5 py-1 rounded-full">Pending Dispatch</span>';

        // Badge Priority Styling
        let priorityBadge = '';
        if (item.priority === 'Express') priorityBadge = '<span class="text-xs font-bold text-red-500">🔴 Express</span>';
        else if (item.priority === 'Standard') priorityBadge = '<span class="text-xs font-bold text-amber-500">🟡 Standard</span>';
        else priorityBadge = '<span class="text-xs font-bold text-emerald-500">🟢 Economy</span>';

        const convertedCost = (item.costUSD * rate).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

        row.innerHTML = `
          <td class="p-4 font-bold text-gray-900 dark:text-white">${item.id}</td>
          <td class="p-4">${item.origin} → ${item.destination}</td>
          <td class="p-4">${item.category}</td>
          <td class="p-4">${priorityBadge}</td>
          <td class="p-4">${statusBadge}</td>
          <td class="p-4 font-semibold text-gray-800 dark:text-gray-200">${symbol}${convertedCost}</td>
          <td class="p-4 text-right rtl:text-left admin-only manager-only">
            <button onclick="deleteShipment('${item.id}')" class="text-red-500 hover:text-red-700 text-xs font-bold hover:underline">Delete</button>
          </td>
        `;

        tbody.appendChild(row);
      });

      document.getElementById('recordCounter').innerText = `${data.length} Records`;
      document.getElementById('paginationInfo').innerText = `Showing 1 to ${data.length} of ${data.length} entries`;

      // Enforce RBAC visibility on rendered DOM elements
      switchRole(currentRole);
    }

    // --- FILTER ENGINE ---
    function applyFilters() {
      const search = document.getElementById('searchInput').value.toLowerCase();
      const cat = document.getElementById('categoryFilter').value;
      const status = document.getElementById('statusFilter').value;
      const prio = document.getElementById('priorityFilter').value;

      const filtered = shipments.filter(item => {
        const matchesSearch = item.id.toLowerCase().includes(search) ||
                              item.origin.toLowerCase().includes(search) ||
                              item.destination.toLowerCase().includes(search);
        const matchesCat = (cat === 'all') || item.category === cat;
        const matchesStatus = (status === 'all') || item.status === status;
        const matchesPrio = (prio === 'all') || item.priority === prio;

        return matchesSearch && matchesCat && matchesStatus && matchesPrio;
      });

      renderTable(filtered);
    }

    // --- CREATE NEW SHIPMENT FORM HANDLER ---
    function handleCreateShipment(e) {
      e.preventDefault();
      
      const newShipment = {
        id: document.getElementById('inputTrackId').value,
        origin: document.getElementById('inputOrigin').value,
        destination: document.getElementById('inputDestination').value,
        category: document.getElementById('inputCategory').value,
        priority: document.getElementById('inputPriority').value,
        status: document.getElementById('inputStatus').value,
        costUSD: parseFloat(document.getElementById('inputCost').value) || 0
      };

      shipments.unshift(newShipment);
      addAuditLog(`New shipment ${newShipment.id} created and set to ${newShipment.status}.`);
      
      closeModal('shipmentModal');
      document.getElementById('newShipmentForm').reset();
      applyFilters();
    }

    // --- DELETE SHIPMENT HANDLER ---
    function deleteShipment(id) {
      if (confirm(`Are you sure you want to delete shipment ${id}?`)) {
        shipments = shipments.filter(s => s.id !== id);
        addAuditLog(`Shipment ${id} was deleted from system.`);
        applyFilters();
      }
    }

    // --- SYSTEM AUDIT STREAM HANDLER ---
    function renderAuditLogs() {
      const container = document.getElementById('auditLogContainer');
      container.innerHTML = '';
      
      auditLogs.forEach(log => {
        const item = document.createElement('div');
        item.className = 'p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg flex items-start space-x-2 rtl:space-x-reverse border border-gray-100 dark:border-gray-800';
        item.innerHTML = `
          <span class="font-bold text-blue-600 dark:text-blue-400 min-w-[55px]">${log.time}</span>
          <span class="text-gray-600 dark:text-gray-300">${log.text}</span>
        `;
        container.appendChild(item);
      });
    }

    function addAuditLog(msg) {
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      auditLogs.unshift({ time: timeStr, text: msg });
      renderAuditLogs();
    }

    function clearLogs() {
      auditLogs = [];
      renderAuditLogs();
    }

    // --- EXPORT TO CSV ENGINE ---
    function exportToCSV() {
      let csvContent = "data:text/csv;charset=utf-8,";
      csvContent += "Tracking ID,Origin,Destination,Category,Priority,Status,Cost (USD)\n";

      shipments.forEach(s => {
        csvContent += `${s.id},${s.origin},${s.destination},${s.category},${s.priority},${s.status},${s.costUSD}\n`;
      });

      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `shipment_report_${new Date().toISOString().slice(0,10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      addAuditLog('System exported active shipment data to CSV.');
    }

    // --- MODAL CONTROLS ---
    function openModal(id) {
      document.getElementById(id).classList.remove('hidden');
    }

    function closeModal(id) {
      document.getElementById(id).classList.add('hidden');
    }

    // --- APPLICATION BOOTSTRAP ---
    document.addEventListener('DOMContentLoaded', () => {
      initCharts();
      renderAuditLogs();
      switchLanguage('en');
      switchRole('admin');
      switchCurrency('USD');
    });
  </script>
</body>
</html>
