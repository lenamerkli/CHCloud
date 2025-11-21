import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-logo',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <span class="logo">
      <span class="ch">CH</span><span class="cloud" [class.dark]="isDark()">Cloud</span>
    </span>
  `,
  styles: `
    .logo {
      font-weight: bold;
      font-size: 1.5rem;
    }
    .ch {
      color: red;
      letter-spacing: 0.1em;
    }
    .cloud {
      color: black;
    }
    .cloud.dark {
      color: white;
    }
  `
})
export class LogoComponent {
  isDark = input<boolean>(false);
}
