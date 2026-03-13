module.exports = {
  apps: [
    {
      name: 'jarvis',
      script: 'venv/bin/gunicorn',
      args: '--workers 4 --threads 2 --bind 127.0.0.1:8000 --timeout 120 --worker-tmp-dir /dev/shm app:app',
      cwd: './',
      interpreter: 'python3', // Use system python to launch gunicorn from venv
      env: {
        NODE_ENV: 'production',
        FLASK_ENV: 'production',
        PORT: '8000'
      },
      log_date_format: 'YYYY-MM-DD HH:mm Z',
      error_file: './logs/error.log',
      out_file: './logs/out.log',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    }
  ]
};
