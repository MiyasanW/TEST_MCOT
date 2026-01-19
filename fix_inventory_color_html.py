
import os
from pathlib import Path

# Path to the template
base_dir = Path("/Users/thanandorn/Desktop/TESTMCOT")
template_path = base_dir / "templates" / "admin" / "inventory_dashboard.html"

# The prompt implementation of the file
# CRITICAL: ALL DJANGO TAGS MUST BE ON ONE LINE.
# FIX: Removed hardcoded 'text-white' from certain elements, creating contrast issues in Light Mode.
# ENSURED: dark:text-white is used where appropriate, and text-gray-900 for light mode.

html_content = """{% extends 'unfold/layouts/base.html' %}
{% load humanize inventory_extras %}

{% block content %}
<div class="min-h-screen p-4 md:p-8 space-y-8 font-sans bg-gray-50/50 dark:bg-gray-900 transition-colors duration-200 ease-in-out">
    
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
            <div class="flex items-center gap-3 group">
                <a href="/admin/" class="p-2 rounded-xl bg-white dark:bg-gray-800 text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 shadow-sm transition-all duration-200">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                    </svg>
                </a>
                <div>
                    <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 tracking-tight">Inventory Dashboard</h1>
                    <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mt-1">Availability for <span class="text-primary-600 dark:text-primary-400 font-bold bg-primary-50 dark:bg-primary-900/20 px-2 py-0.5 rounded-md">{{ pretty_date }}</span></p>
                </div>
            </div>
        </div>

        <form method="get" class="flex items-center gap-3 bg-white dark:bg-gray-800 p-1.5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm transition-all hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600">
            <label for="date" class="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 pl-3">Date</label>
            <input type="date" name="date" id="date" value="{{ selected_date }}" onchange="this.form.submit()" class="block rounded-xl border-gray-200 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm py-2 px-3 bg-white text-gray-900 dark:bg-gray-700 dark:text-white transition-colors cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
        </form>
    </div>

    <!-- Main Content Card -->
    <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden transition-all duration-200 hover:shadow-lg hover:border-gray-200 dark:hover:border-gray-600">
        
        <!-- Table Header -->
        <div class="px-6 py-5 border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 flex justify-between items-center">
            <h3 class="font-bold text-gray-900 dark:text-white">Stock Availability</h3>
            <span class="text-xs font-medium px-2 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400">{{ inventory|length }} Items</span>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead class="bg-gray-50 dark:bg-gray-700/30 text-xs uppercase text-gray-500 dark:text-gray-400 font-semibold tracking-wider sticky top-0 z-10">
                    <tr>
                        <th class="px-6 py-4">Product</th>
                        <th class="px-6 py-4 text-center">Total Stock</th>
                        <th class="px-6 py-4 text-center">Available</th>
                        <th class="px-6 py-4 text-center">Status</th>
                        <th class="px-6 py-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                    {% for item in inventory %}
                    <tr class="group hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors duration-150 cursor-pointer" onclick="document.getElementById('log-{{ item.product.id }}').classList.toggle('hidden')">
                        <td class="px-6 py-4">
                            <div class="flex items-center gap-4">
                                <div class="relative group-hover:scale-105 transition-transform duration-200">
                                    {% if item.product.image %}
                                    <img src="{{ item.product.image.url }}" class="w-12 h-12 rounded-xl object-cover bg-gray-100 dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                                    {% else %}
                                    <div class="w-12 h-12 rounded-xl bg-gray-50 dark:bg-gray-700 flex items-center justify-center border border-gray-100 dark:border-gray-600 text-gray-400">
                                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                    </div>
                                    {% endif %}
                                </div>
                                <div>
                                    <div class="font-bold text-gray-900 dark:text-white text-base group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{{ item.product.name }}</div>
                                    <div class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mt-0.5">{{ item.product.category }}</div>
                                </div>
                            </div>
                        </td>
                        <td class="px-6 py-4 text-center">
                            <span class="font-mono font-bold text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-lg">{{ item.total_stock }}</span>
                        </td>
                        <td class="px-6 py-4 text-center">
                             <div class="flex justify-center">
                                <span class="w-8 h-8 flex items-center justify-center rounded-full text-sm font-bold shadow-sm ring-2 ring-white dark:ring-gray-800 {% if item.available_stock > 0 %}bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300{% else %}bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300{% endif %}">{{ item.available_stock }}</span>
                            </div>
                        </td>
                        <td class="px-6 py-4 text-center">
                            {% if item.available_stock == 0 %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
                                <span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5 animate-pulse"></span> Fully Booked
                            </span>
                            {% else %}
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span> Available
                            </span>
                            {% endif %}
                        </td>
                        <td class="px-6 py-4 text-right">
                             <div class="flex justify-end gap-2 items-center text-xs font-medium text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                                <span>History</span>
                                <svg class="w-4 h-4 transform group-hover:translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Expanded Log Row -->
                    <tr id="log-{{ item.product.id }}" class="hidden transition-all duration-300">
                        <td colspan="5" class="p-0 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                            <div class="p-6 pl-[5.5rem] space-y-4 shadow-inner">
                                <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                                    Transaction Ledger
                                </div>
                                
                                {% if item.ledger %}
                                <div class="relative dark:border-gray-700 space-y-3">
                                    <div class="absolute top-2 left-[7px] bottom-2 w-0.5 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                                    {% for entry in item.ledger %}
                                    <div class="relative pl-6 group/entry">
                                        <div class="absolute left-0 top-3 w-3.5 h-3.5 rounded-full border-2 border-white dark:border-gray-800 bg-gray-300 dark:bg-gray-600 group-hover/entry:bg-primary-500 dark:group-hover/entry:bg-primary-500 transition-colors"></div>
                                        <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center bg-white dark:bg-gray-800/80 p-3 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md hover:border-gray-200 dark:hover:border-gray-600 transition-all">
                                            <div class="min-w-[100px]">
                                                 <span class="block text-xs font-bold text-gray-900 dark:text-white">{{ entry.date_display }}</span>
                                                 <span class="text-[10px] text-gray-400 font-medium uppercase tracking-wide">{{ entry.entry_title }}</span>
                                            </div>
                                            <div class="flex-1">
                                                <p class="text-sm text-gray-600 dark:text-gray-300">{{ entry.detail }}</p>
                                                {% if entry.package_name %}
                                                <div class="flex items-center gap-1 mt-1 text-xs text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 w-fit px-2 py-0.5 rounded-md">
                                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                                                    Pkg: {{ entry.package_name }}
                                                </div>
                                                {% endif %}
                                            </div>
                                            <div class="text-right">
                                                 <span class="font-mono font-bold text-sm px-2 py-1 rounded-lg {% if entry.change > 0 %}bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400{% elif entry.change < 0 %}bg-rose-50 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400{% else %}bg-gray-50 text-gray-500 dark:bg-gray-700 dark:text-gray-400{% endif %}">{{ entry.change }}</span>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                                {% else %}
                                <div class="text-center py-8 rounded-xl border-2 border-dashed border-gray-100 dark:border-gray-700">
                                    <p class="text-sm text-gray-400 dark:text-gray-500">No transactions recorded specific to this date.</p>
                                </div>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 text-xs text-gray-400 dark:text-gray-500 flex justify-between">
            <span>Showing all available inventory</span>
            <span>Real-time availability</span>
        </div>
    </div>
</div>
{% endblock %}
"""

with open(template_path, "w", encoding='utf-8') as f:
    f.write(html_content)

print("Template overwritten successfully with FIXED TEXT COLORS.")
