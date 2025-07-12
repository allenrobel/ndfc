# How other modules can adopt this pattern

## For any new module (networks, interfaces, policies, etc.):

```python
from ansible_collections.cisco.ndfc.plugins.module_utils.common.cache.cached_resource_service import CachedResourceService
from ansible_collections.cisco.ndfc.plugins.module_utils.common.cache.cache_manager import CacheManager

class NetworkApi:
    def __init__(self, ansible_module, cached_service=None):
        # Inject caching service via composition - no inheritance needed!
        if cached_service is None:
            cache_manager = CacheManager(default_ttl_seconds=300)
            self._cached_service = CachedResourceService(cache_manager, "network")
        else:
            self._cached_service = cached_service
        
        # Rest of initialization...
    
    def _fetch_single_network(self, fabric, network_name):
        # Implement API call for single network
        pass
    
    def _fetch_all_networks(self, fabric):
        # Implement API call for all networks
        pass
    
    # Public API methods using composition
    def get_cached(self, fabric, network_name):
        return self._cached_service.get_cached(
            fabric=fabric,
            identifier=network_name,
            fetch_func=lambda: self._fetch_single_network(fabric, network_name)
        )
    
    def get_all_cached(self, fabric):
        return self._cached_service.get_all_cached(
            fabric=fabric,
            fetch_func=lambda: self._fetch_all_networks(fabric)
        )
    
    def exists_cached(self, fabric, network_name):
        return self._cached_service.exists_cached(
            fabric=fabric,
            identifier=network_name,
            fetch_func=lambda: self._fetch_single_network(fabric, network_name)
        )
    
    def create_network(self, payload):
        # Create network...
        success, response = self._execute_request("POST", path, payload)
        
        if success:
            # Automatic cache update
            self._cached_service.update_cache_after_create(
                fabric, network_name, response_data
            )
        
        return success, response
    
    # All other CRUD operations follow the same pattern...

# Usage in main():
def main():
    module = AnsibleModule(...)
    
    # Composition-based dependency injection
    cache_manager = CacheManager(default_ttl_seconds=600)  # 10 minutes for networks
    cached_service = CachedResourceService(cache_manager, "network")
    api_client = NetworkApi(module, cached_service=cached_service)
    
    # Rest of module logic...
```
