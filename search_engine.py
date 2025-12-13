import os

import threading
from datetime import datetime
import pickle

from settings import SEARCH_ROOT, EXCLUDED_PATHS, SEARCH_TOP_K
from path_classifier import get_classifier

# Data paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CACHE_FILE = os.path.join(DATA_DIR, 'search_cache.pkl')
LOG_FILE = os.path.join(DATA_DIR, 'embeddings_log.txt')

class SearchEngine:
    def __init__(self):
        self.file_paths = []
        self.file_names = []
        self.embeddings = None
        self.model = None
        self.is_ready = False
        self.status = "Initializing..."
        self.classifier = get_classifier()  # Path relevance classifier
        
        # Load model in a separate thread so UI opens fast
        self.init_thread = threading.Thread(target=self._initialize_backend)
        self.init_thread.daemon = True
        self.init_thread.start()

    def get_status(self):
        return self.status

    def _log_paths_async(self, paths):
        """Log paths to file asynchronously so it doesn't block anything."""
        def write_log():
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- Embeddings computed at {timestamp} ---\n")
                    for path in paths:
                        f.write(f"{path}\n")
                print(f"Logged {len(paths)} paths to {LOG_FILE}")
            except Exception as e:
                print(f"Error writing log: {e}")
        
        log_thread = threading.Thread(target=write_log)
        log_thread.daemon = True
        log_thread.start()

    def _initialize_backend(self):
        print("Loading Model...")
        self.status = "Downloading Model..."
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

            # 1. Load Cache & Ready Up Immediately
            if self._load_cache():
                print("Loaded index from cache.")
                self._filter_cache()
                self.is_ready = True
                self.status = "Ready"
            
            # 2. Start Background Update (New Files)
            update_thread = threading.Thread(target=self._update_index_background)
            update_thread.daemon = True
            update_thread.start()

        except Exception as e:
            print(f"Error initializing model: {e}")
            self.status = f"Error: {str(e)}"

    def _update_index_background(self):
        """Walks FS in background, finds new files, computes embeddings, and updates state."""
        import numpy as np
        print("Starting background index update...")
        if self.is_ready:
            self.status = "Ready (Scanning for new files...)"
        else:
            self.status = "Indexing Files..."

        # 1. Scan File System
        # Note: This duplicates logic from _index_files but returns a set/list 
        # instead of modifying self state directly initially to avoid race conditions.
        current_paths = []
        current_names = []
        
        try:
            for root, dirs, files in os.walk(SEARCH_ROOT):
                # Check exclusions for root
                is_excluded_root = False
                for excluded in EXCLUDED_PATHS:
                    if root.lower().startswith(excluded.lower()):
                        is_excluded_root = True
                        break
                if is_excluded_root:
                    dirs[:] = []
                    continue

                # Filter directories using classifier
                valid_dirs = []
                for d in dirs:
                    if d.startswith('.'):
                        continue
                    full_path = os.path.join(root, d)
                    # Check absolute path exclusions
                    should_exclude = False
                    for excluded in EXCLUDED_PATHS:
                        if full_path.lower() == excluded.lower():
                            should_exclude = True
                            break
                    if should_exclude:
                        continue
                    # Use classifier
                    if self.classifier.is_relevant(full_path):
                        valid_dirs.append(d)
                        current_paths.append(full_path)
                        current_names.append(d)
                dirs[:] = valid_dirs
                
                # Filter files using classifier
                for f in files:
                    if f.startswith('.'):
                        continue
                    full_path = os.path.join(root, f)
                    if self.classifier.is_relevant(full_path):
                        current_paths.append(full_path)
                        current_names.append(f)
        except Exception as e:
            print(f"Error in background scan: {e}")
            return

        # 2. Compare with existing state
        # Create a map of path -> index or just use set for new file detection
        existing_paths_set = set(self.file_paths)
        
        new_paths = []
        new_names = []
        
        for p, n in zip(current_paths, current_names):
            if p not in existing_paths_set:
                new_paths.append(p)
                new_names.append(n)
        
        if not new_paths:
            print("No new files found.")
            if not self.is_ready: # If we weren't ready (no cache), we are now
                self.file_paths = current_paths
                self.file_names = current_names
                self.is_ready = True 
            self.status = "Ready"
            return
            
        print(f"Found {len(new_paths)} new files.")
        if self.is_ready:
            self.status = f"Ready (Embedding {len(new_paths)} new files...)"
        else:
            self.status = f"Embedding {len(new_paths)} files..."

        # 3. Compute new embeddings
        new_embeddings = self.model.encode(new_names, convert_to_numpy=True, show_progress_bar=True)
        
        # 4. Merge
        # We need to lock or atomic update. 
        # Python lists are thread-safe for extend, but we want to swap pointers references if possible
        # or just append safely.
        
        if self.embeddings is None:
            # First run scenario
            self.file_paths = new_paths
            self.file_names = new_names
            self.embeddings = new_embeddings
        else:
            # Merge scenario
            self.file_paths.extend(new_paths)
            self.file_names.extend(new_names)
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        
        self.is_ready = True
        self.status = "Ready"
        print("Background update complete. Cache saved.")
        self._save_cache()
        
        # Log the new paths asynchronously
        self._log_paths_async(new_paths)

    def _filter_cache(self):
        """Remove excluded paths from the loaded cache to avoid showing unwanted files."""
        if not self.file_paths:
            return

        indices_to_keep = []
        for i, path in enumerate(self.file_paths):
            if self.classifier.is_relevant(path):
                indices_to_keep.append(i)
        
        if len(indices_to_keep) < len(self.file_paths):
            print(f"Filtering {len(self.file_paths) - len(indices_to_keep)} excluded files from cache...")
            self.file_paths = [self.file_paths[i] for i in indices_to_keep]
            self.file_names = [self.file_names[i] for i in indices_to_keep]
            if self.embeddings is not None:
                self.embeddings = self.embeddings[indices_to_keep]
            # Save the cleaned cache
            self._save_cache()

    def _save_cache(self):
        print("Saving cache...")
        prev_status = self.status
        self.status = "Saving Cache..."
        try:
            data = {
                'names': self.file_names,
                'paths': self.file_paths,
                'embeddings': self.embeddings
            }
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(data, f)
            print("Cache saved.")
        except Exception as e:
            print(f"Error saving cache: {e}")
        finally:
            # Restore status (or set to Ready if we were already ready)
            if self.is_ready:
                self.status = "Ready"
            else:
                self.status = prev_status

    def _load_cache(self):
        if not os.path.exists(CACHE_FILE):
            return False
        
        print("Found cache file. Loading...")
        self.status = "Loading from Cache..."
        try:
            with open(CACHE_FILE, 'rb') as f:
                data = pickle.load(f)
                self.file_names = data['names']
                self.file_paths = data['paths']
                self.embeddings = data['embeddings']
            return True
        except Exception as e:
            print(f"Error loading cache: {e}")
            return False

    # Integrated into background update

    def _compute_embeddings(self):
        if not self.file_names:
            return
            
        # sentence-transformers encoding is optimized and simpler
        self.embeddings = self.model.encode(self.file_names, convert_to_numpy=True, show_progress_bar=True)

    def search(self, query, top_k=SEARCH_TOP_K):
        import numpy as np
        if not self.is_ready:
            return [{"name": "System Initializing...", "path": "Please wait for model to load."}]
        
        # Encode query
        query_emb = self.model.encode([query], convert_to_numpy=True)
        
        # Cosine similarity
        # embeddings are already normalized by default in sentence-transformers? 
        # Actually verify: usually encode(normalize_embeddings=True) or manual.
        # But for basic ranking dot product is close enough if we normalize.
        
        # Manual normalization to be safe
        norm_query = np.linalg.norm(query_emb, axis=1, keepdims=True)
        norm_db = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        
        normalized_query = query_emb / (norm_query + 1e-9)
        normalized_db = self.embeddings / (norm_db + 1e-9)
        
        similarities = np.dot(normalized_query, normalized_db.T)[0]
        
        # Top K
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "name": self.file_names[idx],
                "path": self.file_paths[idx],
                "score": float(similarities[idx])
            })
            
        return results
