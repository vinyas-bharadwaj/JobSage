(function(window) {
    'use strict';
    
    window.ExcalidrawWrapper = {
        instances: new Map(),
        isLoaded: false,
        
        init: function(containerId, options = {}, silent = false) {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error('Container not found:', containerId);
                return null;
            }
            
            // Only show loading if not a silent re-initialization
            if (!silent) {
                this.showLoading(container);
            }
            
            // Check if Excalidraw is available
            if (typeof ExcalidrawLib === 'undefined' || !ExcalidrawLib.Excalidraw) {
                console.error('ExcalidrawLib not found');
                this.showError(container, 'Drawing library not loaded');
                return null;
            }
            
            const defaultOptions = {
                initialData: {
                    elements: [],
                    appState: {
                        viewBackgroundColor: "#ffffff",
                        theme: "light",
                        gridSize: null,
                        currentItemFillStyle: "solid",
                        currentItemStrokeWidth: 2,
                        currentItemStrokeColor: "#000000",
                        name: "System Design"
                    }
                },
                onChange: function(elements, appState, files) {
                    console.log('Excalidraw changed:', elements.length, 'elements');
                }
            };
            
            const config = Object.assign({}, defaultOptions, options);
            
            try {
                // Clear container
                container.innerHTML = '';
                
                const excalidrawElement = React.createElement(
                    ExcalidrawLib.Excalidraw,
                    Object.assign({}, config, {
                        ref: (api) => {
                            // Store the API reference for direct manipulation
                            const instance = this.instances.get(containerId);
                            if (instance) {
                                instance.excalidrawAPI = api;
                            }
                        }
                    })
                );
                
                ReactDOM.render(excalidrawElement, container);
                
                // Store instance reference
                this.instances.set(containerId, {
                    container: container,
                    config: config,
                    elements: [],
                    excalidrawAPI: null // Will be set by the ref callback
                });
                
                this.isLoaded = true;
                
                // Return interface with clear method
                return {
                    reinitialize: () => this.reinitialize(containerId),
                    getElements: () => this.getElements(containerId)
                };
                
            } catch (error) {
                console.error('Failed to initialize Excalidraw:', error);
                this.showError(container, 'Failed to initialize drawing tool');
                return null;
            }
        },
        
        reinitialize: function(containerId, silent = false) {
            console.log('Reinitializing Excalidraw for:', containerId);
            const instance = this.instances.get(containerId);
            if (instance) {
                const container = instance.container;
                const config = instance.config;
                
                // Create new config with empty elements
                const newConfig = Object.assign({}, config, {
                    initialData: {
                        elements: [],
                        appState: config.initialData.appState
                    }
                });
                
                // Pass silent flag to init
                return this.init(containerId, newConfig, silent);
            }
            return null;
        },
        
        showLoading: function(container) {
            container.innerHTML = `
                <div class="excalidraw-loading">
                    <div class="spinner"></div>
                    <h4>Loading Drawing Tool...</h4>
                    <p>Please wait while we prepare the drawing interface.</p>
                </div>
            `;
        },
        
        showError: function(container, message) {
            container.innerHTML = `
                <div class="excalidraw-error">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3" style="color: #dc3545;"></i>
                    <h3>Drawing Tool Unavailable</h3>
                    <p>${message || 'Unable to load the drawing interface.'}</p>
                    <button onclick="location.reload()" class="btn btn-primary">
                        <i class="fas fa-sync-alt me-1"></i>Refresh Page
                    </button>
                </div>
            `;
        },
        
        getElements: function(containerId) {
            const instance = this.instances.get(containerId);
            return instance ? instance.elements : [];
        },
        
        updateElements: function(containerId, elements) {
            const instance = this.instances.get(containerId);
            if (instance) {
                instance.elements = elements;
            }
        }
    };
    
})(window);