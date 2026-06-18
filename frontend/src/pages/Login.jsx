import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sprout } from 'lucide-react';
import useAuth from '../hooks/useAuth';
import useToast from '../hooks/useToast';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import AuroraBackground from '../components/common/AuroraBackground';

export function Login() {
  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Invalid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await login(email, password);
      addToast('Welcome back to MediPlant AI!', 'success');
      navigate('/');
    } catch (err) {
      console.error(err);
      const data = err.response?.data;
      let errorMsg = 'Login failed. Please check your credentials.';
      
      if (data?.detail?.errors && Array.isArray(data.detail.errors) && data.detail.errors.length > 0) {
        errorMsg = data.detail.errors[0].message;
      } else if (data?.message) {
        errorMsg = data.message;
      }
      
      addToast(errorMsg, 'error');
      setErrors({ form: errorMsg });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 bg-[#04130a] relative overflow-hidden">
      {/* Global Aurora Background */}
      <AuroraBackground />

      <div className="w-full max-w-md relative z-10">
        {/* Branding header */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary-500/10 text-primary-400 mb-3 border border-primary-500/25 shadow-glow-sm">
            <Sprout className="w-6 h-6 animate-pulse" />
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white">
            Sign in to MediPlant AI
          </h1>
          <p className="mt-2 text-xs text-surface-300">
            Medicinal plant catalog and AI detection assistant
          </p>
        </div>

        {/* Card containing login form */}
        <Card className="shadow-xl p-6 glass border border-white/10">
          <form onSubmit={handleSubmit} className="space-y-4">
            {errors.form && (
              <div className="p-3 text-xs text-red-400 bg-red-950/15 border border-red-900/50 rounded-xl">
                {errors.form}
              </div>
            )}
            
            <Input
              label="Email Address"
              type="email"
              name="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={errors.email}
              required
            />

            <Input
              label="Password"
              type="password"
              name="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={errors.password}
              required
            />

            <Button
              type="submit"
              isLoading={isSubmitting}
              className="w-full shadow-glow py-3 mt-2"
            >
              Sign In
            </Button>
          </form>
        </Card>

        {/* Link to Register */}
        <p className="mt-6 text-center text-xs text-surface-300">
          Don't have an account?{' '}
          <Link
            to="/register"
            className="font-bold text-primary-400 hover:text-primary-350 hover:underline ml-1"
          >
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
