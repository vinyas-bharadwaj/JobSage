(function(window) {
    'use strict';
    
    window.ExcalidrawWrapper = (function() {
        const instances = new Map();
        
        return {
            init: function(containerId, options = {}) {
                const container = document.getElementById(containerId);
                if (!container) {
                    throw new Error(`Container with id "${containerId}" not found`);
                }

                // Check if Excalidraw is available
                if (typeof window.Excalidraw === 'undefined') {
                    console.error('Excalidraw not loaded');
                    return null;
                }

                let excalidrawAPI = null;
                let currentElements = [];
                let currentAppState = {};

                // Create Excalidraw instance - Fixed the reference
                const excalidrawComponent = React.createElement(window.Excalidraw, {
                    onChange: (elements, appState, files) => {
                        currentElements = elements || [];
                        currentAppState = appState || {};
                        
                        // Store in instance
                        const instance = instances.get(containerId);
                        if (instance) {
                            instance.elements = currentElements;
                            instance.appState = currentAppState;
                        }
                        
                        // Call user's onChange if provided
                        if (options.onChange) {
                            options.onChange(elements, appState, files);
                        }
                    },
                    ref: (api) => {
                        excalidrawAPI = api;
                        instances.set(containerId, {
                            api: api,
                            elements: currentElements,
                            appState: currentAppState
                        });
                        console.log('Excalidraw API stored for container:', containerId);
                    }
                });

                // Render the component
                ReactDOM.render(excalidrawComponent, container);

                return excalidrawAPI;
            },

            getElements: function(containerId) {
                const instance = instances.get(containerId);
                if (instance && instance.api) {
                    try {
                        const elements = instance.api.getSceneElements();
                        return elements || [];
                    } catch (e) {
                        console.warn('Error getting elements, using cached:', e);
                        return instance.elements || [];
                    }
                }
                console.warn(`No instance found for container: ${containerId}`);
                return [];
            },

            getAppState: function(containerId) {
                const instance = instances.get(containerId);
                if (instance && instance.api) {
                    try {
                        const appState = instance.api.getAppState();
                        return appState || {};
                    } catch (e) {
                        console.warn('Error getting app state, using cached:', e);
                        return instance.appState || {};
                    }
                }
                console.warn(`No instance found for container: ${containerId}`);
                return {};
            },

            loadScene: function(containerId, elements, appState) {
                const instance = instances.get(containerId);
                if (instance && instance.api) {
                    try {
                        instance.api.updateScene({
                            elements: elements || [],
                            appState: appState || {}
                        });
                        return true;
                    } catch (e) {
                        console.error('Error loading scene:', e);
                        return false;
                    }
                }
                console.warn(`No instance found for container: ${containerId}`);
                return false;
            },

            clear: function(containerId) {
                const instance = instances.get(containerId);
                if (instance && instance.api) {
                    try {
                        instance.api.updateScene({
                            elements: [],
                            appState: {}
                        });
                        return true;
                    } catch (e) {
                        console.error('Error clearing scene:', e);
                        return false;
                    }
                }
                return false;
            }
        };
    })();
    
})(window);