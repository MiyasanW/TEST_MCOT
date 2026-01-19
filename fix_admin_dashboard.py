
import os

content = """{% extends 'unfold/layouts/base.html' %}
{% load static humanize dashboard_tags %}

{% block content %}
{% get_dashboard_stats as stats %}
{% get_recent_bookings 8 as recent_bookings %}

<!-- Chart.js from CDN -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<div class="p-4 md:p-8 space-y-8 font-sans bg-gray-50/50 dark:bg-gray-900 min-h-screen">
    
    <!-- Top Bar: Welcome & Date -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 tracking-tight">
                ยินดีต้อนรับ, {{ user.username }} 👋
            </h1>
            <p class="text-gray-500 dark:text-gray-400 mt-1 text-base font-medium">
                {{ stats.today_thai }} | ภาพรวมระบบ
            </p>
        </div>
        
        <!-- Quick Actions Floating Bar -->
        <div class="flex gap-3 bg-white dark:bg-gray-800 p-1.5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
            <a href="{% url 'inventory_dashboard' %}"
                class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl transition-all">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                Inventory
            </a>
            <a href="{% url 'admin:rentals_booking_add' %}"
                class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 rounded-xl shadow-md transition-all">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                New Booking
            </a>
        </div>
    </div>

    <!-- Alert Section -->
    {% if stats.bookings_pending > 0 %}
    <div class="bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 rounded-2xl p-4 flex items-center justify-between shadow-sm relative overflow-hidden group">
        <div class="absolute inset-0 bg-amber-500/5 group-hover:bg-amber-500/10 transition-colors"></div>
        <div class="flex items-center gap-4 relative z-10">
            <div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-xl text-amber-600 dark:text-amber-400">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            </div>
            <div>
                <h4 class="font-bold text-gray-900 dark:text-white">Attention Needed</h4>
                <p class="text-sm text-gray-600 dark:text-gray-300">
                    You have <strong class="text-amber-600 dark:text-amber-400 underline">{{ stats.bookings_pending }} pending bookings</strong> waiting for review.
                </p>
            </div>
        </div>
        <a href="{% url 'admin:rentals_booking_changelist' %}?status__exact=draft"
            class="relative z-10 text-sm font-semibold bg-white dark:bg-gray-800 text-amber-600 px-4 py-2 rounded-lg shadow-sm hover:shadow active:scale-95 transition-all">
            Review Now &rarr;
        </a>
    </div>
    {% endif %}

    <!-- Key Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Revenue Card -->
        <div class="relative overflow-hidden bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl p-6 text-white shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div class="absolute top-0 right-0 -mt-8 -mr-8 w-32 h-32 bg-white/20 rounded-full blur-2xl"></div>
            <p class="text-emerald-100 font-medium text-sm">Monthly Revenue</p>
            <h3 class="text-3xl font-extrabold mt-1 tracking-tight">{{ stats.revenue_this_month|intcomma }}</h3>
            <div class="mt-4 flex items-center text-emerald-50 text-sm font-medium bg-white/10 w-fit px-2 py-1 rounded-lg">
                <span>Total THB</span>
            </div>
        </div>

        <!-- Bookings Card -->
        <div class="relative overflow-hidden bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl p-6 text-white shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div class="absolute top-0 right-0 -mt-8 -mr-8 w-32 h-32 bg-white/20 rounded-full blur-2xl"></div>
            <p class="text-blue-100 font-medium text-sm">Monthly Bookings</p>
            <h3 class="text-3xl font-extrabold mt-1 tracking-tight">{{ stats.bookings_this_month }}</h3>
            <div class="mt-4 flex items-center text-blue-50 text-sm font-medium bg-white/10 w-fit px-2 py-1 rounded-lg">
                <span>Active Orders</span>
            </div>
        </div>

        <!-- Equipment Card -->
        <div class="bg-white dark:bg-gray-800 rounded-3xl p-6 border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-all">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">Equipment Ready</p>
                    <div class="flex items-baseline gap-1 mt-1">
                        <h3 class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.equipment_available }}</h3>
                        <span class="text-sm text-gray-400">/ {{ stats.equipment_total }}</span>
                    </div>
                </div>
                <div class="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-xl text-purple-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path></svg>
                </div>
            </div>
            <div class="w-full bg-gray-100 dark:bg-gray-700 h-1.5 rounded-full mt-4 overflow-hidden">
                <div class="bg-purple-500 h-full rounded-full" style="width: 75%"></div>
            </div>
        </div>

        <!-- Staff Card -->
        <div class="bg-white dark:bg-gray-800 rounded-3xl p-6 border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-all">
             <div class="flex justify-between items-start">
                <div>
                    <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">Active Staff</p>
                    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ stats.staff_active }}</h3>
                </div>
                <div class="p-2 bg-orange-50 dark:bg-orange-900/20 rounded-xl text-orange-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                </div>
            </div>
            <p class="mt-4 text-xs text-gray-500">Currently online</p>
        </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Revenue Chart -->
        <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-3xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
            <h3 class="font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                <span class="w-2 h-6 bg-primary-500 rounded-full"></span>
                Revenue Trend (7 Days)
            </h3>
            <div class="relative h-64 w-full">
                <canvas id="revenueChart"></canvas>
            </div>
        </div>

        <!-- Status Distribution Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-3xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
            <h3 class="font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                <span class="w-2 h-6 bg-purple-500 rounded-full"></span>
                Booking Status
            </h3>
            <div class="relative h-64 w-full flex items-center justify-center">
                <canvas id="statusChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Recent Bookings Table -->
    <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50">
            <h3 class="font-bold text-gray-900 dark:text-white">Recent Transactions</h3>
            <a href="{% url 'admin:rentals_booking_changelist' %}" class="text-sm font-medium text-primary-600 hover:text-primary-700 hover:underline">View All &rarr;</a>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                <thead class="bg-gray-50 dark:bg-gray-700/50 text-xs uppercase text-gray-700 dark:text-gray-300 font-semibold">
                    <tr>
                        <th class="px-6 py-4">ID</th>
                        <th class="px-6 py-4">Customer</th>
                        <th class="px-6 py-4">Date</th>
                        <th class="px-6 py-4">Total</th>
                        <th class="px-6 py-4">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                    {% for booking in recent_bookings %}
                    <tr class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition duration-150">
                        <td class="px-6 py-4 font-mono font-medium text-gray-900 dark:text-white">#{{ booking.id }}</td>
                        <td class="px-6 py-4">
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-xs font-bold text-gray-500">
                                    {{ booking.created_by.first_name|first|default:"U" }}
                                </div>
                                <span class="font-medium text-gray-900 dark:text-white">{{ booking.created_by.first_name|default:booking.created_by.username }}</span>
                            </div>
                        </td>
                        <td class="px-6 py-4">{{ booking.start_time|date:"d M, H:i" }}</td>
                        <td class="px-6 py-4 font-bold text-emerald-600">{{ booking.calculate_total_price|intcomma }} THB</td>
                        <td class="px-6 py-4">
                            {% if booking.status == 'approved' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">Approved</span>
                            {% elif booking.status == 'draft' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">Draft</span>
                            {% elif booking.status == 'active' %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">Active</span>
                            {% else %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{{ booking.status }}</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="5" class="px-6 py-8 text-center text-gray-400">No recent activity</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

</div>

<!-- Chart Initialization Script -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Revenue Chart
        const ctxRev = document.getElementById('revenueChart').getContext('2d');
        const revData = {{ stats.chart_revenue|safe|default:"[]" }};
        const revLabels = {{ stats.chart_labels|safe|default:"[]" }};
        
        new Chart(ctxRev, {
            type: 'line',
            data: {
                labels: revLabels,
                datasets: [{
                    label: 'Revenue (THB)',
                    data: revData,
                    borderColor: '#10b981', 
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#10b981',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });

        // Status Chart
        const ctxStatus = document.getElementById('statusChart').getContext('2d');
        const statusData = {{ stats.status_counts|safe|default:"{}" }};
        
        new Chart(ctxStatus, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Approved', 'Draft', 'Problem', 'Completed'],
                datasets: [{
                    data: [
                        statusData.active || 0, 
                        statusData.approved || 0, 
                        statusData.draft || 0, 
                        statusData.problem || 0, 
                        statusData.completed || 0
                    ],
                    backgroundColor: [
                        '#8b5cf6', // Purple (Active)
                        '#10b981', // Green (Approved)
                        '#f59e0b', // Amber (Draft)
                        '#ef4444', // Red (Problem)
                        '#3b82f6'  // Blue (Completed)
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } } 
                },
                cutout: '70%',
            }
        });
    });
</script>
{% endblock %}
"""

with open('templates/admin/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully overwrote templates/admin/index.html with {len(content)} bytes.")
