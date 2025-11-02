import { Component } from '@angular/core';
import {MatCard, MatCardContent, MatCardHeader, MatCardTitle} from '@angular/material/card';
import {MatButton} from '@angular/material/button';
import {MatError, MatFormField, MatInput, MatLabel} from '@angular/material/input';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {HttpClient} from '@angular/common/http';
import {Router} from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [
    MatCard,
    MatCardHeader,
    MatCardTitle,
    MatCardContent,
    MatFormField,
    MatLabel,
    MatError,
    MatButton,
    MatInput,
    ReactiveFormsModule
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {

  loginForm!: FormGroup;

  constructor(private formBuilder: FormBuilder, private httpClient: HttpClient, private router: Router) {
    this.initializeForm();
  }

  private initializeForm(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      totpCode: ['', [Validators.required, Validators.pattern(/^\d{6}$/)]]
    });
  }

  onSubmit(): void {
    this.markFormGroupTouched();
    if (this.loginForm.valid) {
      const loginData = {
        email: this.loginForm.value.email,
        password: this.loginForm.value.password,
        totp: this.loginForm.value.totpCode
      };
      this.httpClient.post('/api/login', loginData).subscribe({
        next: (response: any) => {
          if (response.success) {
            this.router.navigate(['/']).then(navigated => {
              if (!navigated) {
                console.error('Navigation failed');
              }
            });
          }
        },
        error: (error) => {
          console.error('Login error:', error);
        }
      });
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.loginForm.controls).forEach(key => {
      const control = this.loginForm.get(key);
      control?.markAsTouched();
    });
  }

  get email() { return this.loginForm.get('email'); }
  get password() { return this.loginForm.get('password'); }
  get totpCode() { return this.loginForm.get('totpCode'); }
}
