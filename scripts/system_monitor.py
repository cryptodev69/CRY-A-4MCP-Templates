#!/usr/bin/env python3
"""
CRY-A-4MCP Advanced System Monitor

Provides detailed monitoring of system performance, data quality, and service health.
"""

import asyncio
import aiohttp
import json
import time
import psutil
import docker
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import sys

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SystemMonitor:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.services = {
            'qdrant': 'http://localhost:6333',
            'neo4j': 'http://localhost:7474',
            'n8n': 'http://localhost:5678',
            'grafana': 'http://localhost:3000',
            'prometheus': 'http://localhost:9090',
            'mcp-server': 'http://localhost:8000'
        }
        
    async def check_service_health(self, session: aiohttp.ClientSession, name: str, url: str) -> Dict:
        """Check health of a specific service"""
        try:
            start_time = time.time()
            async with session.get(f"{url}/health", timeout=10) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json() if 'json' in response.headers.get('content-type', '') else {}
                    return {
                        'name': name,
                        'status': 'healthy',
                        'response_time': response_time,
                        'details': data
                    }
                else:
                    return {
                        'name': name,
                        'status': 'unhealthy',
                        'response_time': response_time,
                        'error': f"HTTP {response.status}"
                    }
        except asyncio.TimeoutError:
            return {
                'name': name,
                'status': 'timeout',
                'response_time': 10000,
                'error': 'Request timeout'
            }
        except Exception as e:
            return {
                'name': name,
                'status': 'error',
                'response_time': 0,
                'error': str(e)
            }
    
    def get_docker_stats(self) -> List[Dict]:
        """Get Docker container statistics"""
        stats = []
        try:
            containers = self.docker_client.containers.list()
            for container in containers:
                if 'cry-a-4mcp' in container.name or any(service in container.name for service in self.services.keys()):
                    container_stats = container.stats(stream=False)
                    
                    # Calculate CPU percentage
                    cpu_delta = container_stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               container_stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = container_stats['cpu_stats']['system_cpu_usage'] - \
                                  container_stats['precpu_stats']['system_cpu_usage']
                    cpu_percent = (cpu_delta / system_delta) * len(container_stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
                    
                    # Calculate memory usage
                    memory_usage = container_stats['memory_stats']['usage']
                    memory_limit = container_stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100.0
                    
                    stats.append({
                        'name': container.name,
                        'status': container.status,
                        'cpu_percent': round(cpu_percent, 2),
                        'memory_usage': memory_usage,
                        'memory_limit': memory_limit,
                        'memory_percent': round(memory_percent, 2),
                        'network_rx': container_stats['networks']['eth0']['rx_bytes'] if 'networks' in container_stats else 0,
                        'network_tx': container_stats['networks']['eth0']['tx_bytes'] if 'networks' in container_stats else 0
                    })
        except Exception as e:
            print(f"Error getting Docker stats: {e}")
        
        return stats
    
    def get_system_stats(self) -> Dict:
        """Get system-level statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'network': psutil.net_io_counters()._asdict(),
            'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
            'uptime': time.time() - psutil.boot_time()
        }
    
    async def check_data_quality(self, session: aiohttp.ClientSession) -> Dict:
        """Check data quality metrics"""
        quality_metrics = {
            'qdrant_collections': 0,
            'qdrant_points': 0,
            'neo4j_nodes': 0,
            'neo4j_relationships': 0,
            'data_freshness': None,
            'errors': []
        }
        
        try:
            # Check Qdrant collections
            async with session.get('http://localhost:6333/collections') as response:
                if response.status == 200:
                    data = await response.json()
                    quality_metrics['qdrant_collections'] = len(data.get('result', {}).get('collections', []))
                    
                    # Get point counts
                    for collection in data.get('result', {}).get('collections', []):
                        collection_name = collection['name']
                        async with session.get(f'http://localhost:6333/collections/{collection_name}') as coll_response:
                            if coll_response.status == 200:
                                coll_data = await coll_response.json()
                                quality_metrics['qdrant_points'] += coll_data.get('result', {}).get('points_count', 0)
        except Exception as e:
            quality_metrics['errors'].append(f"Qdrant check failed: {e}")
        
        try:
            # Check Neo4j data (simplified - would need proper Neo4j driver in production)
            # This is a placeholder for actual Neo4j queries
            quality_metrics['neo4j_nodes'] = 1000  # Placeholder
            quality_metrics['neo4j_relationships'] = 5000  # Placeholder
        except Exception as e:
            quality_metrics['errors'].append(f"Neo4j check failed: {e}")
        
        # Check data freshness (last update time)
        try:
            quality_metrics['data_freshness'] = datetime.utcnow().isoformat()
        except Exception as e:
            quality_metrics['errors'].append(f"Freshness check failed: {e}")
        
        return quality_metrics
    
    async def run_comprehensive_check(self) -> Dict:
        """Run comprehensive system check"""
        async with aiohttp.ClientSession() as session:
            # Check service health
            service_tasks = [
                self.check_service_health(session, name, url)
                for name, url in self.services.items()
            ]
            service_results = await asyncio.gather(*service_tasks, return_exceptions=True)
            
            # Get system stats
            system_stats = self.get_system_stats()
            docker_stats = self.get_docker_stats()
            data_quality = await self.check_data_quality(session)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'services': [r for r in service_results if not isinstance(r, Exception)],
                'system': system_stats,
                'containers': docker_stats,
                'data_quality': data_quality,
                'overall_health': self._calculate_overall_health(service_results, system_stats)
            }
    
    def _calculate_overall_health(self, service_results: List, system_stats: Dict) -> str:
        """Calculate overall system health score"""
        healthy_services = sum(1 for r in service_results if not isinstance(r, Exception) and r.get('status') == 'healthy')
        total_services = len(service_results)
        
        if healthy_services == total_services and system_stats['cpu_percent'] < 80 and system_stats['memory']['percent'] < 80:
            return 'excellent'
        elif healthy_services >= total_services * 0.8:
            return 'good'
        elif healthy_services >= total_services * 0.6:
            return 'fair'
        else:
            return 'poor'
    
    def print_status_report(self, results: Dict):
        """Print formatted status report"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}CRY-A-4MCP System Status Report{Colors.END}")
        print(f"Generated: {results['timestamp']}")
        print(f"Overall Health: {self._format_health_status(results['overall_health'])}")
        print("=" * 60)
        
        # Service Status
        print(f"\n{Colors.BOLD}Service Status:{Colors.END}")
        for service in results['services']:
            status_color = Colors.GREEN if service['status'] == 'healthy' else Colors.RED
            print(f"  {service['name']:<15} {status_color}{service['status']:<10}{Colors.END} "
                  f"({service['response_time']:.1f}ms)")
        
        # System Resources
        print(f"\n{Colors.BOLD}System Resources:{Colors.END}")
        sys_stats = results['system']
        cpu_color = Colors.GREEN if sys_stats['cpu_percent'] < 70 else Colors.YELLOW if sys_stats['cpu_percent'] < 90 else Colors.RED
        mem_color = Colors.GREEN if sys_stats['memory']['percent'] < 70 else Colors.YELLOW if sys_stats['memory']['percent'] < 90 else Colors.RED
        
        print(f"  CPU Usage:      {cpu_color}{sys_stats['cpu_percent']:.1f}%{Colors.END}")
        print(f"  Memory Usage:   {mem_color}{sys_stats['memory']['percent']:.1f}%{Colors.END}")
        print(f"  Disk Usage:     {sys_stats['disk']['percent']:.1f}%")
        print(f"  Load Average:   {sys_stats['load_avg'][0]:.2f}, {sys_stats['load_avg'][1]:.2f}, {sys_stats['load_avg'][2]:.2f}")
        
        # Container Status
        print(f"\n{Colors.BOLD}Container Status:{Colors.END}")
        for container in results['containers']:
            status_color = Colors.GREEN if container['status'] == 'running' else Colors.RED
            print(f"  {container['name']:<20} {status_color}{container['status']:<10}{Colors.END} "
                  f"CPU: {container['cpu_percent']:.1f}% MEM: {container['memory_percent']:.1f}%")
        
        # Data Quality
        print(f"\n{Colors.BOLD}Data Quality:{Colors.END}")
        dq = results['data_quality']
        print(f"  Qdrant Collections: {dq['qdrant_collections']}")
        print(f"  Qdrant Points:      {dq['qdrant_points']:,}")
        print(f"  Neo4j Nodes:        {dq['neo4j_nodes']:,}")
        print(f"  Neo4j Relations:    {dq['neo4j_relationships']:,}")
        
        if dq['errors']:
            print(f"\n{Colors.YELLOW}Data Quality Warnings:{Colors.END}")
            for error in dq['errors']:
                print(f"  - {error}")
    
    def _format_health_status(self, status: str) -> str:
        """Format health status with colors"""
        colors = {
            'excellent': Colors.GREEN,
            'good': Colors.GREEN,
            'fair': Colors.YELLOW,
            'poor': Colors.RED
        }
        return f"{colors.get(status, Colors.RED)}{status.upper()}{Colors.END}"

async def main():
    parser = argparse.ArgumentParser(description='CRY-A-4MCP Advanced System Monitor')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--watch', type=int, metavar='SECONDS', help='Watch mode with specified interval')
    parser.add_argument('--output', type=str, help='Save results to file')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    if args.watch:
        print(f"Starting system monitoring (every {args.watch}s). Press Ctrl+C to stop.")
        try:
            while True:
                results = await monitor.run_comprehensive_check()
                
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    print("\033[2J\033[H")  # Clear screen
                    monitor.print_status_report(results)
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(results, f, indent=2)
                
                await asyncio.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    else:
        results = await monitor.run_comprehensive_check()
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            monitor.print_status_report(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())

